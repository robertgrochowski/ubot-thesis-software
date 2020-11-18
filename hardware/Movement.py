ANGLE_TO_IMPULSES = 0.1
import time
import math

class Movement:
    def __init__(self, enkoder, engines):
        self.enkoder = enkoder
        self.engines = engines

    def turnAngle(self, angle):
        impulses = int(round(angle * ANGLE_TO_IMPULSES))
        print(impulses)

        if angle < 0:
            self.turnLeftImpulses(abs(impulses))
        else:
            self.turnRightImpulses(impulses)

        return impulses

    def moveForward(self):
        self.engines.startForward()

    def moveLeft(self):
        self.engines.startLeftForward()

    def moveRight(self):
        self.engines.startRightForward()

    def stop(self):
        self.engines.stop()

    #####

    def turnLeftImpulses(self, impulses):
        self.enkoder.reset()
        self.engines.startLeftBackward()
        self.engines.startRightForward()
        while (self.enkoder.left < impulses and self.enkoder.right < impulses):
            time.sleep(0.1)

    def turnRightImpulses(self, impulses):
        self.enkoder.reset()
        self.engines.startRightBackward()
        self.engines.startLeftForward()
        while (self.enkoder.left < impulses and self.enkoder.right < impulses):
            time.sleep(0.1)
        self.engines.stop()

    def moveForwardImpulses(self, impulses):
        self.enkoder.reset()
        self.engines.startForward()
        while (self.enkoder.left < impulses and self.enkoder.right < impulses):
            time.sleep(0.1)
        self.engines.stop()

    def moveBackwardImpulses(self, impulses):
        self.enkoder.reset()
        self.engines.startBackward()
        while (self.enkoder.left < impulses and self.enkoder.right < impulses):
            time.sleep(0.1)
        self.engines.stop()


