from enum import Enum
import RPi.GPIO as GPIO


class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    STOP = 0
    FORWARD = 2
    BACKWARD = -2


class Engines:
    def __init__(self, in_a1, in_a2, in_b1, in_b2, pwm_a, pwm_b):
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup((in_a1, in_a2, in_b1, in_b2, pwm_a, pwm_b), GPIO.OUT)
        GPIO.output((in_a1, in_a2, in_b1, in_b2), GPIO.LOW)

        # Setup I/O pins
        self.in_a1 = in_a1
        self.in_a2 = in_a2
        self.in_b1 = in_b1
        self.in_b2 = in_b2
        self.pwm_a = GPIO.PWM(pwm_a, 60)
        self.pwm_b = GPIO.PWM(pwm_b, 60)

        self.b_speed = 0
        self.a_speed = 0
        self.direction = Direction.STOP

        # start PWM
        self.pwm_a.start(self.a_speed)
        self.pwm_b.start(self.b_speed)

    def set_speed(self, speed):
        self.b_speed = speed
        self.a_speed = speed
        self.pwm_b.ChangeDutyCycle(self.b_speed)
        self.pwm_a.ChangeDutyCycle(self.a_speed)

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
        self.direction = Direction.STOP

    def start(self):
        self.pwm_a.start(self.a_speed)
        self.pwm_b.start(self.b_speed)

    def turn_left(self):
        self.start_right_forward()
        self.start_left_backward()
        self.direction = Direction.LEFT

    def turn_right(self):
        self.start_left_forward()
        self.start_right_backward()
        self.direction = Direction.RIGHT

    def set_left_speed(self, speed):
        self.pwm_a.ChangeDutyCycle(speed)

    def set_right_speed(self, speed):
        self.pwm_b.ChangeDutyCycle(speed)

    def start_right_forward(self):
        GPIO.output(self.in_b1, GPIO.LOW)
        GPIO.output(self.in_b2, GPIO.HIGH)
        self.direction = Direction.RIGHT

    def start_left_forward(self):
        GPIO.output(self.in_a1, GPIO.LOW)
        GPIO.output(self.in_a2, GPIO.HIGH)
        self.direction = Direction.LEFT

    def start_right_backward(self):
        GPIO.output(self.in_b1, GPIO.HIGH)
        GPIO.output(self.in_b2, GPIO.LOW)

    def start_left_backward(self):
        GPIO.output(self.in_a1, GPIO.HIGH)
        GPIO.output(self.in_a2, GPIO.LOW)

    def stop_right(self):
        GPIO.output(self.in_b1, GPIO.HIGH)
        GPIO.output(self.in_b2, GPIO.HIGH)

    def stop_left(self):
        GPIO.output(self.in_a1, GPIO.HIGH)
        GPIO.output(self.in_a2, GPIO.HIGH)

