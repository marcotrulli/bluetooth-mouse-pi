#!/usr/bin/env python3
import time
import smbus
import struct
import bluetooth

# -------- MPU6050 Setup --------
class MPU6050:
    def __init__(self, addr=0x68):
        self.bus = smbus.SMBus(1)
        self.addr = addr
        # Wake up MPU6050
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
        return acc_x, acc_y

mpu = MPU6050()
SENS = 5000.0  # regola sensibilità del mouse
time.sleep(1)
print("MPU6050 pronto. Calibrazione iniziale completata.")

# -------- Bluetooth HID Setup --------
# Inserisci qui l'indirizzo Bluetooth del PC target
# Oppure lascia vuoto e fai pairing prima manualmente
BT_ADDR = ""  # lascia vuoto per fare pairing dal PC
BT_PORT = 17  # HID Control Channel (L2CAP)

# Apri socket L2CAP
sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
if BT_ADDR:
    sock.connect((BT_ADDR, BT_PORT))
    print(f"Connesso al PC {BT_ADDR}")
else:
    print("Esegui pairing manuale del Raspberry Pi dal PC prima di inviare movimenti.")

# -------- Funzione per inviare pacchetto mouse --------
def send_mouse(dx, dy, buttons=0):
    """
    Pacchetto HID: [Buttons, Delta X, Delta Y]
    dx, dy = valori da -127 a 127
    """
    dx = max(-127, min(127, dx))
    dy = max(-127, min(127, dy))
    packet = struct.pack("bbb", buttons, dx, dy)
    try:
        sock.send(packet)
    except Exception as e:
        pass  # ignoriamo errori di invio se il PC non è connesso

# -------- Main Loop --------
history_x, history_y = [], []
N = 5  # media mobile per smoothing
try:
    print("Mouse Bluetooth attivo. Muovi il sensore!")
    while True:
        acc_x, acc_y = mpu.get_acceleration()
        dx = int(acc_x / SENS)
        dy = int(acc_y / SENS)

        # smoothing semplice
        history_x.append(dx)
        history_y.append(dy)
        if len(history_x) > N:
            history_x.pop(0)
            history_y.pop(0)
        avg_dx = int(sum(history_x)/len(history_x))
        avg_dy = int(sum(history_y)/len(history_y))

        # invio pacchetto al PC
        send_mouse(avg_dx, -avg_dy)  # Y invertito

        time.sleep(0.02)  # 50Hz
except KeyboardInterrupt:
    print("Chiusura...")
    sock.close()
