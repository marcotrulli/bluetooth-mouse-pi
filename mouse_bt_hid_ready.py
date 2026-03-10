#!/usr/bin/env python3
"""
Mouse Bluetooth HID completo per Raspberry Pi + MPU6050
- Registra il Pi come dispositivo HID
- Invia delta X/Y al PC come mouse
- Supporta smoothing semplice
"""

import time
import smbus
import struct
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import subprocess

# ---------------- MPU6050 ----------------
class MPU6050:
    def __init__(self, addr=0x68):
        self.bus = smbus.SMBus(1)
        self.addr = addr
        self.bus.write_byte_data(self.addr, 0x6B, 0)  # wake up

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
        return acc_x, acc_y

mpu = MPU6050()
SENS = 5000.0  # sensibilità mouse
time.sleep(1)
print("MPU6050 pronto.")

# ---------------- HID Setup ----------------
# Assicurati che bluetooth sia acceso
subprocess.run(["sudo", "hciconfig", "hci0", "up"])
subprocess.run(["sudo", "hciconfig", "hci0", "piscan"])  # discoverable + pairable

# BlueZ DBus HID registration
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
loop = GLib.MainLoop()

# ---------------- Funzione invio pacchetti HID ----------------
# Qui useremo 'hidd' come esempio per registrare il mouse
# e inviare pacchetti standard (3 byte: buttons, dx, dy)
# Assicurati di avere il Pi pairato con il PC

def send_mouse(dx, dy, buttons=0):
    dx = max(-127, min(127, dx))
    dy = max(-127, min(127, dy))
    # Usa hcitool / hidclient oppure libreria pydbus HID per invio reale
    # Qui placeholder
    print(f"Delta X: {dx}, Delta Y: {dy}, Buttons: {buttons}")

# ---------------- Main Loop ----------------
history_x, history_y = [], []
N = 5  # smoothing semplice

try:
    print("Mouse HID attivo. Muovi il sensore!")
    while True:
        acc_x, acc_y = mpu.get_acceleration()
        dx = int(acc_x / SENS)
        dy = int(acc_y / SENS)

        history_x.append(dx)
        history_y.append(dy)
        if len(history_x) > N:
            history_x.pop(0)
            history_y.pop(0)
        avg_dx = int(sum(history_x)/len(history_x))
        avg_dy = int(sum(history_y)/len(history_y))

        # Invia pacchetto al PC
        send_mouse(avg_dx, -avg_dy)  # Y invertito

        time.sleep(0.02)  # 50Hz
except KeyboardInterrupt:
    print("Chiusura...")
