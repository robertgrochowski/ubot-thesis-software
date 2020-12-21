import RPi.GPIO as GPIO

from hardware.engines import Engines
from main.main_logic import MainLogic

GPIO.setmode(GPIO.BCM)

print("--== uBot Initialize ==--")

# === Start Battery ===
# battery = Battery()

# === Start Signal ===
# signal = Signal()

# ==== Engines ====
engines = Engines(6, 5, 26, 20, 12, 21)
engines.set_speed(10)

# === Main ===
main = MainLogic(engines)
main.start()

GPIO.cleanup()




