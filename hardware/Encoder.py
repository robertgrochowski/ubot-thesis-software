import RPi.GPIO as GPIO
encoderDEBUG = False

class Encoder:
    def __init__(self, leftPIN, rightPIN):
        self.leftPIN = leftPIN
        self.rightPIN = rightPIN
        self.right = 0
        self.left = 0

        GPIO.setup(leftPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(rightPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(leftPIN, GPIO.RISING)
        GPIO.add_event_detect(rightPIN, GPIO.RISING)
        GPIO.add_event_callback(leftPIN, self.leftImpulseReceived)
        GPIO.add_event_callback(rightPIN, self.rightImpulseReceived)

    def leftImpulseReceived(self, args):
        if encoderDEBUG:
            print("LEFT IMPULSE")
        self.left += 1

    def rightImpulseReceived(self, args):
        if encoderDEBUG:
            print("RIGHT IMPULSE")
        self.right += 1

    def reset(self):
        self.right = self.left = 0

    def __str__(self):
        return "Left Enkoder = %d\nRight Enkoder = %d" % (self.left, self.right)