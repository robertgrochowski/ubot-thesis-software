import RPi.GPIO as GPIO
ENCODER_DEBUG = False


class Encoder:
    def __init__(self, left_pin, right_pin):
        self.leftPIN = left_pin
        self.rightPIN = right_pin
        self.right = 0
        self.left = 0

        GPIO.setup(left_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(right_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(left_pin, GPIO.RISING)
        GPIO.add_event_detect(right_pin, GPIO.RISING)
        GPIO.add_event_callback(left_pin, self.left_impulse_received)
        GPIO.add_event_callback(right_pin, self.right_impulse_received)

    def left_impulse_received(self, args):
        if ENCODER_DEBUG:
            print("LEFT IMPULSE")
        self.left += 1

    def right_impulse_received(self, args):
        if ENCODER_DEBUG:
            print("RIGHT IMPULSE")
        self.right += 1

    def reset(self):
        self.right = self.left = 0

    def __str__(self):
        return "Left Encoder = %d\nRight Encoder = %d" % (self.left, self.right)
