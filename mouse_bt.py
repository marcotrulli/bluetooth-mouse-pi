import time
from mpu6050_reader import MPU6050

mpu = MPU6050()
SENS = 5000.0  # Regola la sensibilità

print("Partito! Muovi il sensore per vedere i valori:")

try:
    while True:
        acc_x, acc_y, acc_z = mpu.get_acceleration()
        move_x = int(acc_x / SENS)
        move_y = int(acc_y / SENS)
        print(f"Delta X: {move_x}, Delta Y: {move_y}")
        time.sleep(0.05)
except KeyboardInterrupt:
    print("Chiusura...")
