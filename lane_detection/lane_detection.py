import math
import time

import cv2 as cv
import numpy as np
from lane_detection.utils import get_line_from_poly, draw_lines_on_frame, region_of_interest
from lane_detection.detected_line import DetectedLine
from main.config import width, height


class LaneDetection:

    def __init__(self):
        self.preprocessed_frame = None
        self.labeled_frame = None
        # temp
        self.previously_bad = False
        self.last_left_angles = []
        self.last_right_angles = []

    def preprocess_frame(self, frame):
        # 1. Blur
        kernel_size = 5
        blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        # 2. Range
        frame_HSV = cv.cvtColor(blur, cv.COLOR_BGR2HSV)
        in_rng = cv.inRange(frame_HSV, (0, 0, 0), (180, 255, 50))
        # 3. Canny
        canny_image = cv.Canny(in_rng, 200, 0)

        # 4. Crop Canny
        region_of_interest_vertices = [
            (0, height),
            (30, height // 1.75),
            (width - 30, height // 1.75),
            (width, height),
        ]

        cropped_cannyed = region_of_interest(
            canny_image,
            np.array([region_of_interest_vertices], np.int32),
        )
        return cropped_cannyed

    def compute_engines_power(self, left_angle, right_angle):
        left_engine_pwr = 10
        right_engine_pwr = 10

        if left_angle < 50:
            left_engine_pwr = ((50-left_angle)/2)+10

        if right_angle < 50:
            right_engine_pwr = ((50-right_angle)/2)+10

        return left_engine_pwr, right_engine_pwr

    ## TODO Refactor
    def get_line_x(self, angle, point1, point2_y):
        a = math.tan(math.radians(360 - angle))
        b = point1[1] - a * point1[0]
        x = round((point2_y - b) // a)
        return x

    def draw_lane_lines(self, left_angle, right_angle):
        # Left
        point1 = (40, height)
        point2 = (self.get_line_x(left_angle, point1, height - 200), height-200)
        cv.line(self.labeled_frame, point1, point2, [0, 0, 255], 4)

        # Right
        point1 = (width - 40, height)
        point2 = (self.get_line_x(right_angle*-1, point1, height - 200), height - 200)
        cv.line(self.labeled_frame, point1, point2, [0, 0, 255], 4)

    ####

    def process(self, frame):

        if self.previously_bad:
            self.previously_bad = False
            # time.sleep(5)

        # Initialize frame for labeling and preprocessed frame for further processing
        self.labeled_frame = frame.copy()
        self.preprocessed_frame = self.preprocess_frame(frame)

        # Middle line
        cv.line(self.labeled_frame, (int(width // 2), int(height)),
                (int(width // 2), int(height // 2)), [255, 0, 0], 2)

        # Get Edge Lines
        edge_lines = cv.HoughLinesP(
            self.preprocessed_frame,
            rho=2,
            theta=np.pi / 180,
            threshold=10,
            lines=np.array([]),
            minLineLength=10,
            maxLineGap=5
        )

        if edge_lines is None:
            print("Any edge lines found")
            return 0,0

        # Group lines to left and right
        # Calculate score fore each line
        # If score >= 0.8: take this line into account
        computed_lines = []
        computed_lines_left = []
        computed_lines_right = []

        for rawLine in edge_lines:
            for x1, y1, x2, y2 in rawLine:
                line = DetectedLine((x1, y1), (x2, y2))
                computed_lines.append(line)

                if line.side == -1:
                    computed_lines_left.append(line)
                    cv.line(self.labeled_frame, line.point1, line.point2, [0, 0, 255], 2)

                else:
                    computed_lines_right.append(line)
                    cv.line(self.labeled_frame, line.point1, line.point2, [0, 255, 255], 2)

                # cv.line(self.labeled_frame, line.point1, line.point2, (0,255,0), 2)

        if len(computed_lines_left) <= 3 and len(computed_lines_right) <= 3:
            return 0, 0

        if len(computed_lines_left) <= 3:
            return 10, 20

        if len(computed_lines_right) <= 3:
            return 20, 10

        computed_lines_left.sort(key=lambda x: x.angle)
        computed_lines_right.sort(key=lambda x: x.angle)

        left_angle_md = computed_lines_left[len(computed_lines_left)//2].angle
        right_angle_md = computed_lines_right[len(computed_lines_right)//2].angle
        print(left_angle_md)

        self.last_left_angles.append(left_angle_md)
        self.last_right_angles.append(right_angle_md)

        print('----')
        for line in computed_lines_left:
            print(line.angle)

        cv.imshow("dupa", self.preprocessed_frame)
        cv.waitKey(0) & 0xFF

        if len(self.last_left_angles) > 5:
            self.last_left_angles.pop(0)

        if len(self.last_right_angles) > 5:
            self.last_right_angles.pop(0)

        left_avg = sum(self.last_left_angles)//len(self.last_left_angles)
        right_avg = sum(self.last_right_angles)//len(self.last_right_angles)


        # self.draw_lane_lines(left_avg, right_avg)

        cv.putText(self.labeled_frame, "angle: " + str(right_avg), (width - 150, height - 40),
                  cv.FONT_HERSHEY_SIMPLEX, 0.5,
                  (255, 255, 255), 2, cv.LINE_AA)

        cv.putText(self.labeled_frame, "angle: " + str(left_avg), (10, height - 40), cv.FONT_HERSHEY_SIMPLEX,
                   0.5,
                   (255, 255, 255), 2, cv.LINE_AA)

        (left_pwr, right_pwr) = self.compute_engines_power(left_avg, right_avg)

        return left_pwr, right_pwr

    def get_labeled_image(self):
        return self.labeled_frame
