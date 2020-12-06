# import faulthandler; faulthandler.enable()
# test
import RPi.GPIO as GPIO

from hardware.Engines import Engines
from hardware.Encoder import Encoder
from hardware.Movement import Movement
# from VideoProcess import VideoProcess
from lane_detection.MainLogic import MainLogic

GPIO.setmode(GPIO.BCM)

print("--== uBot Initialize ==--")

# === Start Battery ===
# battery = Battery()

# === Start Signal ===
# signal = Signal()

# ==== Engines ====
engines = Engines(6, 5, 26, 20, 12, 21)
engines.setSpeed(10)

# === Encoder ===
encoder = Encoder(24, 23)
movement = Movement(encoder, engines)

# === Video Processing ===
# videoProcessing = VideoProcess(movement)
# videoProcessing.start()
main = MainLogic(movement, engines)
main.start()

GPIO.cleanup()




