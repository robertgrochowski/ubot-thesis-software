import cv2 as cv
import numpy as np
from lane_detection.utils import get_line_from_poly, draw_lines_on_frame, region_of_interest
from lane_detection.detected_line import DetectedLine
from main.config import width, height


class LaneDetection:

    def __init__(self):
        self.preprocessed_frame = None
        self.labeled_frame = None

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
        return cropped_cannyed

    def compute_engines_power(self, diff):
        left_engine_pwr = 0
        right_engine_pwr = 0

        return left_engine_pwr, right_engine_pwr

    def process(self, frame):
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
            threshold=60,
            lines=np.array([]),
            minLineLength=40,
            maxLineGap=5
        )

        if edge_lines is None:
            print("Any edge lines found")
            return self.labeled_frame

        # Group lines to left and right
        # Calculate score fore each line
        # If score >= 0.8: take this line into account
        computed_lines = []
        for rawLine in edge_lines:
            for x1, y1, x2, y2 in rawLine:
                line = DetectedLine((x1, y1), (x2, y2))
                computed_lines.append(line)

                # Draw lines
                color = [255, 0, 255] if line.side == DetectedLine.SIDE_LEFT < 0.8 else [0, 255, 0]
                if line.score < 0.8:
                    continue

                cv.line(self.labeled_frame, line.point1, line.point2, color, 2)

        accurate_lines = list(filter(lambda x: x.score >= 0.8, computed_lines))
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
        edge_lines.append(approx_right_line)
        edge_lines.append(approx_left_line)

        # Draw lines on frame
        self.labeled_frame = draw_lines_on_frame(
            self.labeled_frame,
            [edge_lines],
            thickness=5,
        )

        # COMPUTE
        # -----
        # TODO
        dest_x = (middle_lines_avg[0] + middle_lines_avg[2]) // 2
        diff = width // 2 - dest_x
        # slop = (max_y - min_y) / (right_x_end - right_x_start)
        # cv.putText(frame_lines, str(int(slop)), (self.width // 2 - 30, self.height - 20), cv.FONT_HERSHEY_SIMPLEX, 1,
        #            (255, 255, 255), 2, cv.LINE_AA)
        return self.compute_engines_power(diff)

    def get_labeled_image(self):
        return self.labeled_frame
