import RPi.GPIO as GPIO
from enum import Enum

class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    STOP = 0
    FORWARD = 2
    BACKWARD = -2

class Engines:
    def __init__(self, AIN1, AIN2, BIN1, BIN2, PWMA, PWMB):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup((AIN1, AIN2, BIN1, BIN2, PWMA, PWMB), GPIO.OUT)
        GPIO.output((AIN1, AIN2, BIN1, BIN2), GPIO.LOW)

        self.AIN1 = AIN1
        self.AIN2 = AIN2
        self.BIN1 = BIN1
        self.BIN2 = BIN2
        self.PWMA = GPIO.PWM(PWMA, 60)
        self.PWMB = GPIO.PWM(PWMB, 60)

        self.Bspeed = 0
        self.Aspeed = 0

        self.direction = Direction.STOP

        self.PWMA.start(self.Aspeed)
        self.PWMB.start(self.Bspeed)

    def setSpeed(self, speed):
        self.Bspeed = speed
        self.Aspeed = speed
        self.PWMB.ChangeDutyCycle(self.Bspeed)
        self.PWMA.ChangeDutyCycle(self.Aspeed)

    def startForward(self):
        self.startRightForward()
        self.startLeftForward()
        self.direction = Direction.FORWARD

    def startBackward(self):
        self.startRightBackward()
        self.startLeftBackward()
        self.direction = Direction.BACKWARD

    def stop(self):
        self.stopRight()
        self.stopLeft()
        # self.PWMA.stop()
        # self.PWMB.stop()
        self.direction = Direction.STOP

    def start(self):
        self.PWMA.start(self.Aspeed)
        self.PWMB.start(self.Bspeed)

    def turnLeft(self):
        self.startRightForward()
        self.startLeftBackward()
        self.direction = Direction.LEFT

    def turnRight(self):
        self.startLeftForward()
        self.startRightBackward()
        self.direction = Direction.RIGHT

    def setLeftSpeed(self, speed):
        self.PWMA.ChangeDutyCycle(speed)

    def setRightSpeed(self, speed):
        self.PWMB.ChangeDutyCycle(speed)

    #####

    def startRightForward(self):
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)
        self.direction = Direction.RIGHT
        # self.start()

    def startLeftForward(self):
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        self.direction = Direction.LEFT
        # self.start()

    def startRightBackward(self):
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.LOW)
        # self.start()

    def startLeftBackward(self):
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        # self.start()

    def stopRight(self):
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.HIGH)
        # self.start()

    def stopLeft(self):
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.HIGH)
        # self.start()


