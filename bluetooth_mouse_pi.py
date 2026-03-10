#!/usr/bin/env python3
import time
import smbus
import bluetooth

# ---------------- MPU6050 ----------------
class MPU6050:
    def __init__(self, addr=0x68):
        self.bus = smbus.SMBus(1)
        self.addr = addr
        self.bus.write_byte_data(self.addr, 0x6B, 0)

    def read_raw_data(self, reg):
        high = self.bus.read_byte_data(self.addr, reg)
        low = self.bus.read_byte_data(self.addr, reg+1)
        value = (high << 8) | low
        if value > 32768:
            value -= 65536
        return value

    def get_delta(self, sens=5000.0):
        acc_x = self.read_raw_data(0x3B)
        acc_y = self.read_raw_data(0x3D)
        dx = int(acc_x / sens)
        dy = int(acc_y / sens)
        return dx, dy

# ---------------- Bluetooth client ----------------
PC_BT_ADDR = "XX:XX:XX:XX:XX:XX"  # indirizzo PC Bluetooth
PORT = 3  # porta RFCOMM, da scegliere libera

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
try:
    sock.connect((PC_BT_ADDR, PORT))
    print(f"Connesso al PC {PC_BT_ADDR}:{PORT}")
except bluetooth.btcommon.BluetoothError as e:
    print("Errore connessione Bluetooth:", e)
    exit(1)

mpu = MPU6050()
time.sleep(1)
print("MPU6050 pronto. Calibrazione iniziale completata.")

history_x, history_y = [], []
N = 5  # smoothing

try:
    while True:
        dx, dy = mpu.get_delta()
        history_x.append(dx)
        history_y.append(dy)
        if len(history_x) > N:
            history_x.pop(0)
            history_y.pop(0)
        avg_dx = int(sum(history_x)/len(history_x))
        avg_dy = int(sum(history_y)/len(history_y))

        # invia pacchetto al PC
        msg = f"{avg_dx},{avg_dy}\n"
        sock.send(msg.encode())

        time.sleep(0.02)  # 50Hz
except KeyboardInterrupt:
    print("Chiusura...")
    sock.close()
