from lidar import Lidar
import socket
import struct

SENSOR_DEV = "/dev/serial0"
SENSOR_BAUDRATE = 460800
SENSOR_PRECISION = 0.1
HORIZ_SERVO = 18
VERT_SERVO = 12
VERT_OFFSET = 10

SCAN_RANGE_THETA = (-30, 30)
SCAN_RANGE_PHI = (0, 30)
SCAN_THETA_POINTS = 240
SCAN_PHI_POINTS = 240
SCAN_STEP_TIME = 0.01

print("Initializing")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    def process_datapoint(x: float, y: float, z: float, strength: int, temp: float) -> None:
        # Just send 3 raw floats per data point for now
        sock.sendall(struct.pack("ddd", x, y, z))
    lidar = Lidar(SENSOR_DEV, SENSOR_BAUDRATE, SENSOR_PRECISION, HORIZ_SERVO, VERT_SERVO, VERT_OFFSET, process_datapoint)

    host, port = input("Enter host & port for processing server: ").split(":")
    port = int(port)
    # NOTE: Setting the socket to be nonblocking after this might be needed for performance
    sock.connect((host, port))
    print("Connected")

    lidar.reset()
    input("Zero ok? Press enter to confirm")

    input("System ready. Press enter to start scan")
    lidar.scan_v(SCAN_RANGE_THETA[0], SCAN_RANGE_THETA[1], SCAN_RANGE_PHI[0], SCAN_RANGE_PHI[1],
                 (SCAN_RANGE_THETA[1] - SCAN_RANGE_THETA[0]) / SCAN_THETA_POINTS,
                 (SCAN_RANGE_PHI[1] - SCAN_RANGE_PHI[0]) / SCAN_PHI_POINTS,
                 SCAN_STEP_TIME, print_progress=True)
    print("Scan done, zeroing")
    lidar.reset()
    input("Zero done")
