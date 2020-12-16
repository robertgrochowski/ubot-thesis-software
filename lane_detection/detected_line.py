from main.config import width, height
import math
import cv2 as cv

class DetectedLine:
    SIDE_LEFT = -1
    SIDE_RIGHT = 1

    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

        self.x_score = 0
        self.y_score = 0
        self.total_diff = 0
        self.total_dist = 0

        self.angle = 0

        self.side = 0
        self.score = 0
        self.calculate_score_and_side()

    def calculate_score_and_side(self):
        (x1, y1) = self.point1
        (x2, y2) = self.point2

        self.y_score = (abs(y2 + y1) // 2) / height
        self.x_score = 0
        if x1 < width // 2 and x2 < width // 2:
            self.x_score = (width - (abs(x2 + x1) // 2)) / width
            self.side = DetectedLine.SIDE_LEFT

        elif x1 > width // 2 and x2 > width // 2:
            self.x_score = (abs(x2 + x1) // 2) / width
            self.side = DetectedLine.SIDE_RIGHT

        self.score = self.y_score + self.x_score

        # calculate angle
        dt_y = abs(y2 - y1)
        dt_x = abs(x2 - x1)
        if dt_y == 0:
            self.angle = 90

        self.angle = round(math.degrees(math.atan(dt_x / dt_y)))
        a = (y1-y2)/(x1-x2)

        # TODO!!!
        if self.side == -1 and a > 0:
            self.angle *= -1

        if self.side == 1 and a < 0:
            self.angle *= -1

    def calculate_total_diff(self, avg_x, avg_y):
        self.total_diff = abs(self.x_score-avg_x) + abs(self.y_score-avg_y)

    def to_line(self):
        return (self.point1[0], self.point1[1], self.point2[0], self.point2[1])

    def calculate_distance(self, lines):
        i = 0
        for line in lines:
            if line.side == self.side:
                dis = self.dist(self.to_line(), line.to_line())
                self.total_dist += dis
                # print(f"Adding dist: {dis}")
                i+=1

    def dist(self, line1, line2):
        line1_x = (line1[0] + line1[2]) // 2
        line1_y = (line1[1] + line1[3]) // 2
        line2_x = (line2[0] + line2[2]) // 2
        line2_y = (line2[1] + line2[3]) // 2

        return (line1_x-line2_x)**2 + abs(line1_y-line2_y)**2
