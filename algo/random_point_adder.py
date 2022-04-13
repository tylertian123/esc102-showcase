import struct
import numpy as np
import socket
import time

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", 4206))
        while True:
            x, y, z = np.random.rand(3)
            start = time.time()
            sock.send(struct.pack("ddd", x, y, z))
            time.sleep(0.1)
