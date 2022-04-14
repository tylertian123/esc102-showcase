from typing import Callable
import tfmini_s
import gpiozero
import time
import math
import threading
import sys


# Set pin factory to pigpio according to the docs to reduce jitter
gpiozero.Device.pin_factory = gpiozero.pins.pigpio.PiGPIOFactory()


class Lidar:

    # Note the callback will be called from a separate thread!
    def __init__(self, sensor_device: str, sensor_baudrate: int, horiz_servo_port: int, vert_servo_port: int,
                 data_callback: Callable[[float, float, float], None]) -> None:
        self.sensor = tfmini_s.Sensor(sensor_device, sensor_baudrate)
        # Pulse width range 500us to 2500us
        # Frame width of 3ms inferred from operating frequency range (50Hz-330Hz)
        self.h_servo = gpiozero.AngularServo(horiz_servo_port, initial_angle=0, min_angle=-135, max_angle=135,
            min_pulse_width=500e-6, max_pulse_width=2500e-6, frame_width=4e-3)
        self.v_servo = gpiozero.AngularServo(vert_servo_port, initial_angle=0, min_angle=0, max_angle=270,
            min_pulse_width=500e-6, max_pulse_width=2500e-6, frame_width=4e-3)
        self.callback = data_callback
        # Used by the daemon
        self.h_angle = 0
        self.v_angle = 0
        self.scanning = False

    def reset(self) -> None:
        """
        Reset servo angles.
        """
        self.h_servo.angle = 0
        self.v_servo.angle = 0
        self.h_angle = self.v_angle = 0

    def move_to_angle(self, h_angle: float, v_angle: float) -> None:
        """
        Move the servos to a specific angle.
        """
        self.h_servo.angle = h_angle
        self.v_servo.angle = v_angle
        self.h_angle = h_angle
        self.v_angle = v_angle
    
    def _sensor_daemon(self):
        """
        Daemon thread for reading sensor data so the servos don't slow down.

        Relies on the GIL so that setting values are atomic operations.
        """
        self.sensor.clear_buf()
        while self.scanning:
            # If more than 2 readings are in the buffer, discard them so we get the latest values
            clear_buf = self.sensor.readings_avail() > 2
            # TODO: Add error handling for r being -1, once stuff on the sensor end is figured out
            for _ in range(5):
                try:
                    r, strength, temp = self.sensor.read(clear_buf)
                    break
                except tfmini_s.ChecksumError:
                    pass
            else:
                print("[LiDAR] Error: Repeated checksum errors!", file=sys.stderr)
                raise RuntimeError("Repeated checksum errors when communicating with ranging sensor!")
            if r == -1:
                print(f"[LiDAR] Warning: Could not read distance (strength={strength}, temp={temp})", file=sys.stderr)
            theta = math.radians(self.h_angle)
            phi = math.radians(self.v_angle)
            self.callback(r * math.cos(phi) * math.cos(theta), r * math.cos(phi) * math.sin(theta), r * math.sin(phi))

    def scan_h(self, start_angle_h: float, stop_angle_h: float, start_angle_v: float, stop_angle_v: float,
               h_step: float, v_step: float, step_time: float) -> None:
        """
        Perform a full scan in the angle range specified, sweeping horizontally first.

        start_angle_h, stop_angle_h: Start and stop horizontal angles (left-right axis).
        start_angle_v, stop_angle_v: Start and stop vertical angles (up-down axis).
        h_step: Angle increment between data points horizontally.
        v_step: Angle increment between data points vertically.
        step_time: The amount of time to wait between two data points for the servo to move into position,
            for the slower axis.
        """
        # Move servos into initial position and wait
        self.move_to_angle(start_angle_h, start_angle_v)
        time.sleep(1)

        self.scanning = True
        # Start the daemon
        th = threading.Thread(target=self._sensor_daemon)
        th.setDaemon(True)
        th.start()

        while self.v_servo.angle < stop_angle_v:
            # Scan in both directions
            while (h_step > 0 and self.h_servo.angle < stop_angle_h) or (h_step < 0 and self.h_servo.angle > start_angle_h):
                self.h_angle += h_step
                self.h_servo.angle = self.h_angle

            # Change stepping direction and move slow axis
            h_step = -h_step
            self.v_angle += v_step
            self.v_servo.angle = self.v_angle
            time.sleep(step_time)

        self.scanning = False
    
    def scan_v(self, start_angle_h: float, stop_angle_h: float, start_angle_v: float, stop_angle_v: float,
               h_step: float, v_step: float, step_time: float) -> None:
        """
        Same as scan_h(), but sweeps vertically first.
        """
        self.move_to_angle(start_angle_h, start_angle_v)
        time.sleep(1)

        self.scanning = True
        th = threading.Thread(target=self._sensor_daemon)
        th.setDaemon(True)
        th.start()

        while self.h_servo.angle < stop_angle_h:
            # Scan in both directions
            while (v_step > 0 and self.v_servo.angle < stop_angle_v) or (v_step < 0 and self.v_servo.angle > start_angle_v):
                self.v_angle += v_step
                self.v_servo.angle = self.v_angle

            # Change stepping direction and move slow axis
            v_step = -v_step
            self.h_angle += h_step
            self.h_servo.angle = self.h_angle
            time.sleep(step_time)

        self.scanning = False
