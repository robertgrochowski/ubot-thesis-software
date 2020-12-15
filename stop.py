import RPi.GPIO as GPIO
from hardware.engines import Engines
GPIO.setmode(GPIO.BCM)
engines = Engines(6,5,26,20,12,21)
engines.stop()
GPIO.cleanup()  