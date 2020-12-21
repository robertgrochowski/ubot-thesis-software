from main.config import SIDE_LEFT, SIDE_RIGHT, HALF_WIDTH
import math


class DetectedLine:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

        self.middle_point = ((point1[0] + point2[0]) // 2, (point1[1] + point2[1]) // 2)
        self.side = SIDE_LEFT if self.middle_point[0] < HALF_WIDTH else SIDE_RIGHT

        self.angle = self.calculate_angle()

    def calculate_angle(self):
        (x1, y1) = self.point1
        (x2, y2) = self.point2

        dt_y = float(abs(y2 - y1))
        dt_x = float(x2 - x1)
        return round(math.degrees(math.atan(dt_x / dt_y))) if dt_y != 0 else 90

    def is_left(self):
        return self.side == SIDE_LEFT

    def is_right(self):
        return self.side == SIDE_RIGHT

    def to_line(self):
        return self.point1[0], self.point1[1], self.point2[0], self.point2[1]

    def __lt__(self, other):
        return self.angle < other.angle
