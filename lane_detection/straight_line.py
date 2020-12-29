class StraightLine:
    a = None
    b = None

    def __init__(self, a, b):
        self.a = round(a, 6)
        self.b = round(b, 6)

    @classmethod
    def from_ab(cls, a, b):
        return StraightLine(a, b)

    @classmethod
    def from_2points(cls, x_a, y_a, x_b, y_b):
        a = (y_a - y_b) / (x_a - x_b)
        b = y_a - a * x_a
        return StraightLine(a, b)

    def get_segment_from_y_points(self, y1, y2):
        point1 = [self.get_x(y1), y1]
        point2 = [self.get_x(y2), y2]
        return point1 + point2

    def get_segment_from_x_points(self, x1, x2):
        point1 = [x1, self.get_y(x1)]
        point2 = [x2, self.get_y(x2)]
        return point1 + point2

    def get_x(self, y):
        poly_x = (y - self.b) / self.a
        return int(poly_x)

    def get_y(self, x):
        return self.a*x + self.b

    def get_horizontal_distance_from_point(self, point):
        return int(abs(point[0] - self.get_x(point[1])))
