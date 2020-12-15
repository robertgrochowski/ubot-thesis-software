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
        self.engines.start_forward()

    def moveLeft(self):
        self.engines.start_left_forward()

    def moveRight(self):
        self.engines.start_right_forward()

    def stop(self):
        self.engines.stop()

    #####

    def turnLeftImpulses(self, impulses):
        self.enkoder.reset()
        self.engines.start_left_backward()
        self.engines.start_right_forward()
        while (self.enkoder.left < impulses and self.enkoder.right < impulses):
            time.sleep(0.1)

    def turnRightImpulses(self, impulses):
        self.enkoder.reset()
        self.engines.start_right_backward()
        self.engines.start_left_forward()
        while (self.enkoder.left < impulses and self.enkoder.right < impulses):
            time.sleep(0.1)
        self.engines.stop()

    def moveForwardImpulses(self, impulses):
        self.enkoder.reset()
        self.engines.start_forward()
        while (self.enkoder.left < impulses and self.enkoder.right < impulses):
            time.sleep(0.1)
        self.engines.stop()

    def moveBackwardImpulses(self, impulses):
        self.enkoder.reset()
        self.engines.start_backward()
        while (self.enkoder.left < impulses and self.enkoder.right < impulses):
            time.sleep(0.1)
        self.engines.stop()


