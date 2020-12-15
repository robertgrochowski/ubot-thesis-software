import time

from picamera.array import PiRGBArray
from picamera import PiCamera
from lane_detection.lane_detection import LaneDetection
from main.config import width, height
import cv2 as cv


class MainLogic:

    def __init__(self, movement, engines):
        self.running = True

        self.laneDetection = LaneDetection()
        self.signDetection = None  # todo
        self.movement = movement
        self.engines = engines

        self.camera = PiCamera()
        self.camera.resolution = (width, height)
        self.camera.framerate = 20
        self.rawCapture = PiRGBArray(self.camera, size=(width, height))

    def start(self):
        # allow the camera to warmup
        time.sleep(0.3)

        while self.running:
            for img in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
                frame = img.array

                # clear the stream in preparation for the next frame
                self.rawCapture.truncate(0)

                # monitor for quit
                k = cv.waitKey(1) & 0xFF
                if k == ord('q'):
                    self.running = False
                    break

                (left_motor_pwr, right_motor_pwr) = self.laneDetection.process(frame)
                print(f"({left_motor_pwr}, {right_motor_pwr})")

                cv.imshow("Preview", self.laneDetection.get_labeled_image())

        cv.destroyAllWindows()