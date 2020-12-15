from main.config import width, height


class DetectedLine:
    SIDE_LEFT = -1
    SIDE_RIGHT = 1

    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        self.side = 0
        self.score = 0
        self.calculate_score_and_side()

    def calculate_score_and_side(self):
        (x1, y1) = self.point1
        (x2, y2) = self.point2

        if x1 < width // 2 and x2 < width // 2:
            y_score = (abs(y2 + y1) // 2) / height
            x_score = (width - (abs(x2 + x1) // 2)) / width
            self.score = y_score + x_score
            self.side = DetectedLine.SIDE_LEFT
        elif x1 > width // 2 and x2 > width // 2:
            y_score = (abs(y2 + y1) // 2) / height
            x_score = (abs(x2 + x1) // 2) / width
            self.score = y_score + x_score
            self.side = DetectedLine.SIDE_RIGHT
