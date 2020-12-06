import RPi.GPIO as GPIO
import time
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from hardware.Engines import Engines
from hardware.Encoder import Encoder
from hardware.Movement import Movement

GPIO.setmode(GPIO.BCM)

print("-- Drive Test Start --")

# ==== Engines ====
engines = Engines(6, 5, 26, 20, 12, 21)
engines.setSpeed(40)

# === Encoder ===
encoder = Encoder(24, 23)
movement = Movement(encoder, engines)

print("-- Moving Left --")
movement.moveLeft()
time.sleep(2)
movement.stop()
time.sleep(1)

print("-- Moving Right --")
movement.moveRight()
time.sleep(2)
movement.stop()
time.sleep(1)

print("-- Moving Forward --")
movement.moveForward()
time.sleep(2)
movement.stop()

GPIO.cleanup()
