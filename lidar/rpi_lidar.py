from lidar import Lidar
import socket
import struct

SENSOR_DEV = ""
SENSOR_BAUDRATE = 115200
HORIZ_SERVO = 0
VERT_SERVO = 0

SCAN_RANGE_THETA = (-30, 30)
SCAN_RANGE_PHI = (0, 60)
SCAN_THETA_POINTS = 120
SCAN_PHI_POINTS = 120
SCAN_THETA_STEP_TIME = 0.1
SCAN_PHI_STEP_TIME = 0.1

print("Initializing")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    def process_datapoint(x: float, y: float, z: float) -> None:
        # Just send 3 raw floats per data point for now
        sock.sendall(struct.pack("ddd", x, y, z))
    lidar = Lidar(SENSOR_DEV, SENSOR_BAUDRATE, HORIZ_SERVO, VERT_SERVO, process_datapoint)

    host, port = input("Enter host & port for processing server: ").split(":")
    port = int(port)
    # NOTE: Setting the socket to be nonblocking after this might be needed for performance
    sock.connect((host, port))
    print("Connected")

    lidar.reset()
    input("Zero ok? Press enter to confirm")

    input("System ready. Press enter to start scan")
    lidar.scan(SCAN_RANGE_THETA[0], SCAN_RANGE_THETA[1], SCAN_RANGE_PHI[0], SCAN_RANGE_PHI[1],
            (SCAN_RANGE_THETA[1] - SCAN_RANGE_THETA[0]) / SCAN_THETA_POINTS,
            (SCAN_RANGE_PHI[1] - SCAN_RANGE_PHI[0]) / SCAN_PHI_POINTS,
            SCAN_THETA_STEP_TIME, SCAN_PHI_STEP_TIME)
    print("Scan done")
