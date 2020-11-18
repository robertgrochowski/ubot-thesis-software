import RPi.GPIO as GPIO
import time
from Engines import Engines
from Encoder import Encoder
from Movement import Movement

GPIO.setmode(GPIO.BCM)

print("start")

# === Start Battery ===
# battery = Battery()

# === Start Signal ===
# signal = Signal()

# ==== Engines ====
engines = Engines(6, 5, 26, 20, 12, 21)
engines.setSpeed(40)

# === Enkoder ===
enkoder = Encoder(24, 23)
movement = Movement(enkoder, engines)

movement.moveLeft()
time.sleep(2)
movement.stop()
time.sleep(1)
movement.moveRight()
time.sleep(2)
movement.stop()
time.sleep(1)
movement.moveForward()
time.sleep(2)
movement.stop()

GPIO.cleanup()


