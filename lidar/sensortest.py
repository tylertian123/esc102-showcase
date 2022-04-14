import tfmini_s
import time

sensor = tfmini_s.Sensor("/dev/ttyUSB0")

sensor.clear_buf()
cmd = b"\x5A\x06\x03\xE8\x03\x4E"
print(sensor.ser.write(cmd))
sensor.ser.flush()

num_readings = 0
sensor.clear_buf()

t = time.time()
while True:
    dist, strength, temp = sensor.read()
    num_readings += 1
    if num_readings % 50 == 0:
        print(dist)
        diff = time.time() - t
        t = time.time()
        print(f"Rate: {50 / diff}Hz")
