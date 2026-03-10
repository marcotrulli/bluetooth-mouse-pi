import smbus

class MPU6050:
    def __init__(self, addr=0x68):
        self.bus = smbus.SMBus(1)
        self.addr = addr
        # Sveglia il sensore
        self.bus.write_byte_data(self.addr, 0x6B, 0)

    def read_raw_data(self, reg):
        high = self.bus.read_byte_data(self.addr, reg)
        low = self.bus.read_byte_data(self.addr, reg + 1)
        value = (high << 8) | low
        if value > 32768:
            value -= 65536
        return value

    def get_acceleration(self):
        acc_x = self.read_raw_data(0x3B)
        acc_y = self.read_raw_data(0x3D)
        acc_z = self.read_raw_data(0x3F)
        return acc_x, acc_y, acc_z
