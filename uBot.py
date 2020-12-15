# import faulthandler; faulthandler.enable()
# test
import RPi.GPIO as GPIO

from hardware.engines import Engines
from hardware.encoder import Encoder
from hardware.movement import Movement
# from VideoProcess import VideoProcess
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

# === Encoder ===
encoder = Encoder(24, 23)
movement = Movement(encoder, engines)

# === Video Processing ===
# videoProcessing = VideoProcess(movement)
# videoProcessing.start()
main = MainLogic(movement, engines)
main.start()

GPIO.cleanup()




