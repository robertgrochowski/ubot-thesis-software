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
        self.signDetection = None #SignDetection()
        self.movement = movement
        self.engines = engines

        self.camera = PiCamera()
        self.camera.resolution = (width, height)
        self.camera.framerate = 20
        self.rawCapture = PiRGBArray(self.camera, size=(width, height))

    def start(self):
        # allow the camera to warmup
        time.sleep(1)

        #self.engines.start()
        #self.movement.moveForward()
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
                #
                (left_motor_pwr, right_motor_pwr) = self.laneDetection.process(frame)
                #print(f"({left_motor_pwr}, {right_motor_pwr})")
                self.engines.set_left_speed(left_motor_pwr)
                self.engines.set_right_speed(right_motor_pwr)
                img = self.laneDetection.get_labeled_image()
                cv.putText(img, "pwr: " + str(right_motor_pwr), (width - 75, height - 20),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5,
                           (255, 255, 0), 2, cv.LINE_AA)

                cv.putText(img, "pwr: " + str(left_motor_pwr), (10, height - 20), cv.FONT_HERSHEY_SIMPLEX,
                           0.5,
                           (255, 255, 0), 2, cv.LINE_AA)

                cv.imshow("Preview", img)

        cv.destroyAllWindows()
        self.engines.stop()
