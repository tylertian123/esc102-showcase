from typing import Callable
import tfmini_s
import gpiozero
import time
import math


# Set pin factory to pigpio according to the docs to reduce jitter
gpiozero.Device.pin_factory = gpiozero.pins.pigpio.PiGPIOFactory()


class Lidar:

    def __init__(self, sensor_device: str, sensor_baudrate: int, horiz_servo_port: int, vert_servo_port: int,
                 data_callback: Callable[[float, float, float], None]) -> None:
        self.sensor = tfmini_s.Sensor(sensor_device, sensor_baudrate)
        # Pulse width range 500us to 2500us
        # Frame width of 3ms inferred from operating frequency range (50Hz-330Hz)
        self.h_servo = gpiozero.AngularServo(horiz_servo_port, initial_angle=0, min_angle=-135, max_angle=-135,
            min_pulse_width=500e-6, max_pulse_width=2500e-6, frame_width=4e-3)
        self.v_servo = gpiozero.AngularServo(vert_servo_port, initial_angle=0, min_angle=0, max_angle=270,
            min_pulse_width=500e-6, max_pulse_width=2500e-6, frame_width=4e-3)
        self.callback = data_callback

    def reset(self) -> None:
        """
        Reset servo angles.
        """
        self.h_servo.angle = 0
        self.v_servo.angle = 0

    def move_to_angle(self, h_angle: float, v_angle: float) -> None:
        """
        Move the servos to a specific angle.
        """
        self.h_servo.angle = h_angle
        self.v_servo.angle = v_angle

    def scan(self, start_angle_h: float, stop_angle_h: float, start_angle_v: float, stop_angle_v: float,
             h_step: float, v_step: float, h_step_time: float, v_step_time: float) -> None:
        """
        Perform a full scan in the angle range specified.

        start_angle_h, stop_angle_h: Start and stop horizontal angles (left-right axis).
        start_angle_v, stop_angle_v: Start and stop vertical angles (up-down axis).
        h_step: Angle increment between data points horizontally.
        v_step: Angle increment between data points vertically.
        h_step_time: The amount of time to wait between two data points for the servo to move into position,
            for horizontal movements.
        v_step_time: The amount of time to wait between two data points for the servo to move into position,
            for vertical movements.
        """
        # Move servos into initial position and wait
        self.h_servo.angle = start_angle_h
        self.v_servo.angle = start_angle_v
        time.sleep(1)
        while self.v_servo.angle < stop_angle_v:
            # Scan in both directions
            phi = math.radians(self.v_servo.angle)
            while (h_step > 0 and self.h_servo.angle < stop_angle_h) or (h_step < 0 and self.h_servo.angle > start_angle_h):
                self.h_servo.angle += h_step
                time.sleep(h_step_time)
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
                    raise RuntimeError("Repeated checksum errors when communicating with ranging sensor!")
                theta = math.radians(self.h_servo.angle)
                self.callback(r * math.cos(phi) * math.cos(theta), r * math.cos(phi) * math.sin(theta), r * math.sin(phi))
            # Change stepping direction and move rows
            h_step = -h_step
            self.v_servo.angle += v_step
            time.sleep(v_step_time)
