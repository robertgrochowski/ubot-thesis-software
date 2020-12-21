import time

from picamera.array import PiRGBArray
from picamera import PiCamera
from lane_detection.lane_detection import LaneDetection
from main.config import *
import cv2 as cv


class MainLogic:

    def __init__(self, engines):
        self.running = True

        self.laneDetection = LaneDetection()
        self.signDetection = None
        self.engines = engines

        self.camera = PiCamera()
        self.camera.resolution = (WIDTH, HEIGHT)
        self.camera.framerate = 20
        self.rawCapture = PiRGBArray(self.camera, size=(WIDTH, HEIGHT))

    def start(self):
        # allow the camera to warmup
        time.sleep(1)

        out = None if not RECORD else cv.VideoWriter(RECORD_FILENAME,
                                                     cv.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                                     10,
                                                     (WIDTH, HEIGHT))
        self.engines.start_forward()
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

                # Set motors power
                (left_motor_pwr, right_motor_pwr) = self.laneDetection.process(frame)

                self.engines.set_left_speed(left_motor_pwr)
                self.engines.set_right_speed(right_motor_pwr)

                # label image
                img = self.laneDetection.get_labeled_image()
                img = self.draw_engines_power(img, left_motor_pwr, right_motor_pwr)
                cv.imshow("uBot eyes", img)

                if RECORD:
                    out.write(img)

        if RECORD:
            out.release()

        cv.destroyAllWindows()
        self.engines.stop()

    def draw_engines_power(self, img, left_motor_pwr, right_motor_pwr):
        img = cv.putText(img, "pwr: " + str(right_motor_pwr), (WIDTH - 75, HEIGHT - 20),
                         cv.FONT_HERSHEY_SIMPLEX, 0.5,
                         (255, 255, 0), 2, cv.LINE_AA)

        img = cv.putText(img, "pwr: " + str(left_motor_pwr), (10, HEIGHT - 20), cv.FONT_HERSHEY_SIMPLEX,
                         0.5,
                         (255, 255, 0), 2, cv.LINE_AA)
        return img
