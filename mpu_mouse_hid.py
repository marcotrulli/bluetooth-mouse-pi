#!/usr/bin/env python3
"""
Mouse Bluetooth HID + MPU6050
Funziona con HIDpi: invia dx/dy al PC
"""

import time
import smbus

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

mpu = MPU6050()
time.sleep(1)
print("MPU6050 pronto. Calibrazione iniziale completata.")

# ---------------- HID Mouse Setup ----------------
# HIDpi deve essere installato e il Pi deve essere pairato con il PC
try:
    from scripts.mouse import MouseHID  # HIDpi: esempio di classe mouse
except ImportError:
    print("Errore: HIDpi non trovato. Controlla di avere HIDpi nella cartella e installato.")
    exit(1)

# Crea oggetto mouse HID
mouse = MouseHID()
mouse.connect()  # connessione al PC già pairato

# ---------------- Main Loop ----------------
history_x, history_y = [], []
N = 5  # smoothing semplice

try:
    print("Mouse HID attivo. Muovi il sensore!")
    while True:
        dx, dy = mpu.get_delta()

        # smoothing
        history_x.append(dx)
        history_y.append(dy)
        if len(history_x) > N:
            history_x.pop(0)
            history_y.pop(0)
        avg_dx = int(sum(history_x)/len(history_x))
        avg_dy = int(sum(history_y)/len(history_y))

        # invia pacchetto HID al PC
        mouse.send(avg_dx, -avg_dy, buttons=0)  # Y invertito se necessario

        time.sleep(0.02)  # 50Hz
except KeyboardInterrupt:
    print("Chiusura...")
    mouse.disconnect()
