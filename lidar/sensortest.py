import tfmini_s
import time

sensor = tfmini_s.Sensor("/dev/serial0", 460800)

num_readings = 0
sensor.clear_buf()

t = time.time()
while True:
    dist, strength, temp = sensor.read()
    num_readings += 1
    if num_readings % 50 == 0:
        print(f"Distance {dist}cm, strength {strength}, temp {temp}C")
        diff = time.time() - t
        t = time.time()
        print(f"Rate: {50 / diff}Hz")
