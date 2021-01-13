import cv2 as cv
from .utils import draw_lines_on_frame, region_of_interest, get_opposite_side
from .detected_line import DetectedLine
from .straight_line import StraightLine
from main.config import *


class LaneDetection:

    def __init__(self):
        self.preprocessed_frame = None
        self.labeled_frame = None
        self.iterations = 0
        self.last_biases = []

        self.last_linear_function = dict()

    def preprocess_frame(self, frame):
        # 1. Grayscale
        grayscale = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # 2. Blur
        kernel_size = 11
        blur = cv.GaussianBlur(grayscale, (kernel_size, kernel_size), 0)
        # 3. Canny
        canny_image = cv.Canny(blur, 200, 0)
        # 4. Crop Canny
        cropped_cannyed = region_of_interest(
            canny_image,
            np.array([REGION_OF_INTEREST], np.int32),
        )

        return cropped_cannyed

    def compute_engines_power(self, bias):
        side_right = bias < 0
        bias = abs(bias)

        if bias < MIN_BIAS_DIST:
            return INITIAL_POWER_LEFT, INITIAL_POWER_RIGHT

        bias = min(bias, MAX_BIAS_DIST)
        add = abs(bias) / MAX_BIAS_DIST * MAX_ADDITIONAL_POWER

        if side_right:
            return INITIAL_POWER_LEFT+add, INITIAL_POWER_RIGHT
        else:
            return INITIAL_POWER_LEFT, INITIAL_POWER_RIGHT+add

    def process(self, frame):
        self.iterations += 1

        # Initialize frame for labeling and preprocessed frame for further processing
        self.labeled_frame = frame.copy()
        self.preprocessed_frame = self.preprocess_frame(frame)

        # Draw middle line
        cv.line(self.labeled_frame, (HALF_WIDTH, HEIGHT), (HALF_WIDTH, HALF_HEIGHT), (255, 0, 0), 2)

        # Get Edge Lines
        edge_lines = cv.HoughLinesP(
            self.preprocessed_frame,
            rho=HOUGH_RHO,
            theta=HOUGH_THETA,
            threshold=HOUGH_THRESHOLD,
            lines=np.array([]),
            minLineLength=HOUGH_MIN_LINE_LENGTH,
            maxLineGap=HOUGH_MAX_LINE_GAP
        )

        if edge_lines is None:
            self.draw_center_text("no lines found")
            return 0, 0

        computed_lines = dict()
        computed_lines[SIDE_LEFT] = []
        computed_lines[SIDE_RIGHT] = []

        for raw_line in edge_lines:
            for x1, y1, x2, y2 in raw_line:
                line = DetectedLine((x1, y1), (x2, y2))

                # If we do not have last linear functions defined yet
                # Skip measuring (let them build themself firstly)
                if len(self.last_linear_function) < 1:
                    computed_lines[line.side].append(line)
                    continue

                # If detected line is too close to the opposite line, ignore it
                # (filtering process)
                if self.last_linear_function[get_opposite_side(line.side)]\
                       .get_horizontal_distance_from_point(line.middle_point) > MIN_DISTANCE_FROM_OPPOSITE_LINE:
                    computed_lines[line.side].append(line)
                    color = LINE_CORRECT_LEFT_COLOR if line.is_left() else LINE_CORRECT_RIGHT_COLOR
                else:
                    color = LINE_IGNORED_LEFT_COLOR if line.is_left() else LINE_IGNORED_RIGHT_COLOR

                cv.line(self.labeled_frame, line.point1, line.point2, color, thickness=2)

        # Measure the quantity of the valid data we have collected so far.
        # If quantity of lines is insufficient, move motors in side calculated by function below
        # in order to collect more lines in next iteration.
        power = self.get_motors_power_if_insufficient_data(computed_lines)
        if power is not None:
            return power

        # Sort our lines by their angle
        for side in sorted(computed_lines):
            computed_lines[side] = sorted(computed_lines[side])

        # Pick median line
        md_line = dict()
        md_line[SIDE_LEFT] = computed_lines[SIDE_LEFT][len(computed_lines[SIDE_LEFT]) // 2]
        md_line[SIDE_RIGHT] = computed_lines[SIDE_RIGHT][len(computed_lines[SIDE_RIGHT]) // 2]

        # Build linear functions from two points
        linear_function = dict()
        linear_function[SIDE_LEFT] = StraightLine.from_2points(
            x_a=md_line[SIDE_LEFT].point1[0],
            y_a=md_line[SIDE_LEFT].point1[1],
            x_b=md_line[SIDE_LEFT].point2[0],
            y_b=md_line[SIDE_LEFT].point2[1])

        linear_function[SIDE_RIGHT] = StraightLine.from_2points(
            x_a=md_line[SIDE_RIGHT].point1[0],
            y_a=md_line[SIDE_RIGHT].point1[1],
            x_b=md_line[SIDE_RIGHT].point2[0],
            y_b=md_line[SIDE_RIGHT].point2[1])

        # Build left, middle and right lines from linear functions
        approx_left_line = linear_function[SIDE_LEFT].get_segment_from_y_points(APPROX_LINE_MIN_Y, APPROX_LINE_MAX_Y)
        approx_right_line = linear_function[SIDE_RIGHT].get_segment_from_y_points(APPROX_LINE_MIN_Y, APPROX_LINE_MAX_Y)
        middle_line = self.get_line_between(approx_left_line, approx_right_line)

        # Draw lines on frame
        self.labeled_frame = draw_lines_on_frame(
            self.labeled_frame,
            [[middle_line, approx_right_line, approx_left_line]],
            thickness=5,
        )

        # Check if lines are really close to each other
        distance = abs(
            (approx_left_line[0] + approx_left_line[2] // 2) - ((approx_right_line[0] + approx_right_line[2]) // 2))

        # When left line is too near to right line
        # if so, use data from previous iteration
        if self.iterations >= ITERATIONS_TO_STORE_LINEAR_FUNC:
            if distance < MAX_DISTANCE_BETWEEN_LINES:
                middle_line = self.get_line_between(self.last_linear_function[SIDE_LEFT],
                                                    self.last_linear_function[SIDE_RIGHT])
            else:
                self.last_linear_function = linear_function

        bias = self.get_bias(middle_line)
        return self.compute_engines_power(bias)

    def get_labeled_image(self):
        return self.labeled_frame

    def draw_center_text(self, text, color=(0, 0, 255), size=0.5):
        cv.putText(self.labeled_frame, text, (HALF_WIDTH - 50, HALF_HEIGHT),
                   cv.FONT_HERSHEY_SIMPLEX, size, color, 2, cv.LINE_AA)

    def get_line_between(self, left_line, right_line):
        return [(left_line[0] + right_line[0]) // 2, APPROX_LINE_MIN_Y,
                (left_line[2] + right_line[2]) // 2, APPROX_LINE_MAX_Y]

    def get_motors_power_if_insufficient_data(self, computed_lines):
        # Stop if there are no valid lines
        if len(computed_lines[SIDE_LEFT]) < MIN_VALID_LINES_PER_SIDE and \
                len(computed_lines[SIDE_RIGHT]) < MIN_VALID_LINES_PER_SIDE:
            self.draw_center_text("no valid lines")
            return 0, 0

        # Move right if there is no left lines
        elif len(computed_lines[SIDE_LEFT]) < MIN_VALID_LINES_PER_SIDE:
            self.draw_center_text("no left lines")
            return ENGINES_POWER_NO_LEFT_LINES

        # Move left if there is no right lines
        elif len(computed_lines[SIDE_RIGHT]) < MIN_VALID_LINES_PER_SIDE:
            self.draw_center_text("no right lines")
            return ENGINES_POWER_NO_RIGHT_LINES

        # Return none if we have sufficient data
        return None

    def get_bias(self, middle_line):
        p2 = (middle_line[0], APPROX_LINE_MAX_Y)
        p1 = (middle_line[2], APPROX_LINE_MIN_Y)
        bias = HALF_WIDTH - ((p1[0] + p2[0]) // 2)

        cv.putText(self.labeled_frame, "bias: "+str(bias), (HALF_WIDTH - 30, HEIGHT - 40),
                   fontFace=cv.FONT_HERSHEY_SIMPLEX,
                   fontScale=0.7,
                   color=(255, 255, 255),
                   thickness=2,
                   lineType=cv.LINE_AA)

        cv.circle(self.labeled_frame, (int(HALF_WIDTH - bias), int((APPROX_LINE_MAX_Y + APPROX_LINE_MIN_Y) // 2)),
                  radius=5,
                  color=(0, 0, 255),
                  thickness=5)

        # Get bias of last few measures
        self.last_biases.append(bias)
        if len(self.last_biases) > BIAS_AVERAGES_COUNT:
            self.last_biases.pop(0)

        return round(sum(self.last_biases) / len(self.last_biases))