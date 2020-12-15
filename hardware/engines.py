from enum import Enum
import RPi.GPIO as GPIO


class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    STOP = 0
    FORWARD = 2
    BACKWARD = -2


class Engines:
    def __init__(self, ain1, ain2, bin1, bin2, pwm_a, pwm_b):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup((ain1, ain2, bin1, bin2, pwm_a, pwm_b), GPIO.OUT)
        GPIO.output((ain1, ain2, bin1, bin2), GPIO.LOW)

        self.AIN1 = ain1
        self.AIN2 = ain2
        self.BIN1 = bin1
        self.BIN2 = bin2
        self.PWMA = GPIO.PWM(pwm_a, 60)
        self.PWMB = GPIO.PWM(pwm_b, 60)

        self.Bspeed = 0
        self.Aspeed = 0

        self.direction = Direction.STOP

        self.PWMA.start(self.Aspeed)
        self.PWMB.start(self.Bspeed)

    def set_speed(self, speed):
        self.Bspeed = speed
        self.Aspeed = speed
        self.PWMB.ChangeDutyCycle(self.Bspeed)
        self.PWMA.ChangeDutyCycle(self.Aspeed)

    def start_forward(self):
        self.start_right_forward()
        self.start_left_forward()
        self.direction = Direction.FORWARD

    def start_backward(self):
        self.start_right_backward()
        self.start_left_backward()
        self.direction = Direction.BACKWARD

    def stop(self):
        self.stop_right()
        self.stop_left()
        # self.PWMA.stop()
        # self.PWMB.stop()
        self.direction = Direction.STOP

    def start(self):
        self.PWMA.start(self.Aspeed)
        self.PWMB.start(self.Bspeed)

    def turn_left(self):
        self.start_right_forward()
        self.start_left_backward()
        self.direction = Direction.LEFT

    def turn_right(self):
        self.start_left_forward()
        self.start_right_backward()
        self.direction = Direction.RIGHT

    def set_left_speed(self, speed):
        if speed > 100: speed = 100
        self.PWMA.ChangeDutyCycle(speed)

    def set_right_speed(self, speed):
        if speed > 100: speed = 100
        self.PWMB.ChangeDutyCycle(speed)

    #####

    def start_right_forward(self):
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)
        self.direction = Direction.RIGHT
        # self.start()

    def start_left_forward(self):
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        self.direction = Direction.LEFT
        # self.start()

    def start_right_backward(self):
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.LOW)
        # self.start()

    def start_left_backward(self):
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        # self.start()

    def stop_right(self):
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.HIGH)
        # self.start()

    def stop_left(self):
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.HIGH)
        # self.start()
