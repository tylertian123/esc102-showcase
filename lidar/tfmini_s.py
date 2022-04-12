from typing import Tuple
import serial


class ChecksumError(Exception):
    """
    Indicates that the checksum was incorrect, possibly due to a hardware issue in the serial line.
    """


class Sensor:
    """
    TFmini-S LiDAR sensor over serial.
    """

    def __init__(self, device: str, baudrate: int = 115200):
        self.ser = serial.Serial(device, baudrate, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

    def read(self) -> Tuple[float, int, float]:
        """
        Read a distance value (in meters).

        This method blocks until a value is ready.

        Returns a tuple of (distace, strength, temp) where distance is in meters, strength is between 0 and 65535,
        and temp is in degrees Celsius. If strength < 100, the detection is considered unstable and the returned
        distance will be -1.

        Raises ChecksumError on checksum mismatch.
        """
        # Format: 0x59 0x59 Dist_L Dist_H Strength_L Strength_H Temp_L Temp_H Checksum
        # First read bytes until we see the full header
        start_byte_count = 0
        while True:
            b = self.ser.read()
            if b == b'\x59':
                start_byte_count += 1
                if start_byte_count == 2:
                    break
            else:
                start_byte_count = 0
                print("[Warning] TFmini-S Serial: Discarded byte", b)
        # Read the next 7 bytes
        data = self.ser.read(6)
        # Note unpacking the bytes here turns them into ints
        dist_l, dist_h, strength_l, strength_h, temp_l, temp_h = data
        checksum = self.ser.read()
        # Check checksum
        if (0x59 * 2 + sum(data)) & 0xFF != int.from_bytes(checksum, byteorder="little"):
            raise ChecksumError(f"Checksum {checksum} does not match expected value 0x{(0x59 * 2 + sum(data)) & 0xFF:02x}")
        temp = ((temp_h << 8) | temp_l) / 8 - 256
        # TODO: Figure out if distance is mapped correctly here
        # TODO: When strength < 100, distance should be -1, figure out how that's represented
        # TODO: Implement the other cases, when distance is -2 (signal strength saturation) and -4 (ambient light saturation)
        dist = ((dist_h << 8) | dist_l) / 65535 * 12
        strength = ((strength_h << 8) | strength_l)
        return dist, strength, temp
