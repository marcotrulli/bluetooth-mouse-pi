#!/usr/bin/env python3
import time
import smbus
import socket

# ---------------- MPU6050 ----------------
class MPU6050:
    def __init__(self, addr=0x68):
        self.bus = smbus.SMBus(1)
        self.addr = addr
        self.bus.write_byte_data(self.addr, 0x6B, 0)  # wake up

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

# ---------------- TCP client ----------------
PC_IP = "192.168.1.100"  # indirizzo IP del PC
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PC_IP, PORT))
print(f"Connesso al PC {PC_IP}:{PORT}")

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

        msg = f"{avg_dx},{avg_dy}\n"
        sock.send(msg.encode())
        time.sleep(0.02)
except KeyboardInterrupt:
    print("Chiusura...")
    sock.close()
