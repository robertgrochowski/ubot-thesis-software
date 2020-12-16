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
            (30, height // 2),
            (width - 30, height // 2),
            (width, height),
        ]

        cropped_cannyed = region_of_interest(
            canny_image,
            np.array([region_of_interest_vertices], np.int32),
        )
        cv.imshow("dupa", cropped_cannyed)
        return cropped_cannyed

    def compute_engines_power(self, diff):
        left_engine_pwr = 0
        right_engine_pwr = 0
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
            return self.labeled_frame

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
                else:
                    computed_lines_right.append(line)

                cv.line(self.labeled_frame, line.point1, line.point2, (0,255,0), 2)

        computed_lines_left.sort(key=lambda x: x.angle)
        computed_lines_right.sort(key=lambda x: x.angle)

        left_angle_md = computed_lines_left[len(computed_lines_left)//2].angle
        right_angle_md = computed_lines_right[len(computed_lines_right)//2].angle

        self.last_left_angles.append(left_angle_md)
        self.last_right_angles.append(right_angle_md)
        if len(self.last_left_angles) > 10:
            self.last_left_angles.pop(0)

        if len(self.last_right_angles) > 10:
            self.last_right_angles.pop(0)

        left_avg = sum(self.last_left_angles)//len(self.last_left_angles)
        right_avg = sum(self.last_right_angles)//len(self.last_right_angles)


        self.draw_lane_lines(left_avg, right_avg)

        cv.putText(self.labeled_frame, "angle: " + str(right_avg), (width - 150, height - 40),
                  cv.FONT_HERSHEY_SIMPLEX, 0.5,
                  (255, 255, 255), 2, cv.LINE_AA)

        cv.putText(self.labeled_frame, "angle: " + str(left_avg), (10, height - 40), cv.FONT_HERSHEY_SIMPLEX,
                   0.5,
                   (255, 255, 255), 2, cv.LINE_AA)

        # for line in computed_lines:
        #     # Draw lines
        #     color = [0, 255, 0] if line.total_diff < 0.3 else [0, 0, 255]
        #     cv.line(self.labeled_frame, line.point1, line.point2, color, 2)
        #     if line.total_diff > 0.3:
        #         cv.putText(self.labeled_frame, str(line.total_diff), line.point1, cv.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1,
        #                cv.FONT_HERSHEY_PLAIN)
        #
        #     line.calculate_distance(computed_lines)
        #
        #     print()

        accurate_lines = list(filter(lambda x: x.total_diff <= 0.3, computed_lines))
        accurate_lines_left = list(filter(lambda x: x.side == DetectedLine.SIDE_LEFT, accurate_lines))
        accurate_lines_right = list(filter(lambda x: x.side == DetectedLine.SIDE_RIGHT, accurate_lines))

        if not accurate_lines_left or not accurate_lines_right:
            print("No accurate left/right line found")
            return self.labeled_frame

        # Collect left lines coordination's
        left_x = np.array([[_line.point1[0], _line.point2[0]] for _line in accurate_lines_left]).flatten()
        left_y = np.array([[_line.point1[1], _line.point2[1]] for _line in accurate_lines_left]).flatten()

        # Collect right lines coordination's
        right_x = np.array([[_line.point1[0], _line.point2[0]] for _line in accurate_lines_right]).flatten()
        right_y = np.array([[_line.point1[1], _line.point2[1]] for _line in accurate_lines_right]).flatten()

        # Find best polynomial fit for left and right line
        accurate_lines_left_poly = np.poly1d(np.polyfit(
            left_y,
            left_x,
            deg=1
        ))

        accurate_lines_right_poly = np.poly1d(np.polyfit(
            right_y,
            right_x,
            deg=1
        ))

        edge_lines = []
        min_y = frame.shape[0] * (3 / 5)  # Just below the horizon
        max_y = frame.shape[0]  # The bottom of the image

        # Build Left, Middle and Right lines from poly
        approx_left_line = get_line_from_poly(accurate_lines_left_poly, max_y, min_y)
        approx_right_line = get_line_from_poly(accurate_lines_right_poly, max_y, min_y)
        middle_lines_avg = [(approx_left_line[0] + approx_right_line[0]) // 2, max_y,
                            (approx_left_line[2] + approx_right_line[2]) // 2, min_y]

        # Add all lines to the lines collection
        edge_lines.append(middle_lines_avg)
        # edge_lines.append(approx_right_line)
        # edge_lines.append(approx_left_line)

        # Draw lines on frame
        self.labeled_frame = draw_lines_on_frame(
            self.labeled_frame,
            [edge_lines],
            thickness=5,
        )

        # COMPUTE
        # -----
        dest_x = (middle_lines_avg[0] + middle_lines_avg[2]) // 2
        diff = width // 2 - dest_x
        cv.putText(self.labeled_frame, str(int(diff)), (width // 2 - 30, height - 20), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv.LINE_AA)

        (left_pwr, right_pwr) = self.compute_engines_power(diff)

        cv.putText(self.labeled_frame, "pwr: "+str(left_pwr), (width - 75, height - 20), cv.FONT_HERSHEY_SIMPLEX, 0.5,
                   (255, 0, 0), 2, cv.LINE_AA)

        cv.putText(self.labeled_frame, "pwr: " + str(right_pwr), (10, height - 20), cv.FONT_HERSHEY_SIMPLEX,
                   0.5,
                   (255, 0, 0), 2, cv.LINE_AA)

        return left_pwr, right_pwr

    def get_labeled_image(self):
        return self.labeled_frame
