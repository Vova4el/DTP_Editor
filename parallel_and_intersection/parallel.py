class Parallel():
    def __init__(self, mint1, mint2,width,height):
        self.point1 = mint1
        self.point2 = mint2
        self.point3 = mint2
        self.point4 = mint1
        self.xx = self.point1[0] - self.point2[0]
        self.yy = self.point1[1] - self.point2[1]
        self.tx = self.xx
        self.ty = self.yy
        self.xx2 = self.point3[0] - self.point4[0]
        self.yy2 = self.point3[1] - self.point4[1]
        self.tx2 = self.xx2
        self.ty2 = self.yy2
        self.points1 = []
        self.points2 = []
        self.fs1_n_line = False
        self.fs2_n_line = False
        self.width = width
        self.height = height

    def line_intersects_segment(self,A, B, C, x1, y1, x2, y2):
        """ Проверяет, пересекает ли прямая Ax + By + C = 0 отрезок (x1, y1) - (x2, y2) """

        def line_equation(x, y):
            return A * x + B * y + C

        # Значения функции для концов отрезка
        f1 = line_equation(x1, y1)
        f2 = line_equation(x2, y2)

        # Проверка, лежат ли концовые точки отрезка на одной стороне прямой
        if f1 == 0 or f2 == 0:
            return True
        if f1 * f2 < 0:
            return True

        # Проверка пересечения
        return False

    def does_line_intersect_square(self, P1, P2, square):
        """ Проверяет, пересекает ли прямая любую из сторон квадрата """
        # square - список вершин квадрата [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        # Определяем стороны квадрата как отрезки
        # Распаковка координат точек прямой
        x1, y1 = P1
        x2, y2 = P2

        # Коэффициенты уравнения прямой
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2
        for i in range(4):
            x1, y1 = square[i]
            x2, y2 = square[(i + 1) % 4]
            if self.line_intersects_segment(A, B, C, x1, y1, x2, y2):
                return True
        return False

    def add_new_line(self):
        while (0 <= (self.point1[0] + self.xx) <= self.width or 0 <= (self.point1[1] + self.yy) <= self.height or
               self.fs1_n_line == True):
            self.points1.append((self.point1[0] + self.xx, self.point1[1] + self.yy))
            self.xx += self.tx
            self.yy += self.ty
            if self.fs1_n_line ==True:
                continue
        if self.fs1_n_line == False:
            self.xx -= self.tx
            self.yy -= self.ty
        self.fs1_n_line = False


        while (0 <= (self.point3[0] + self.xx2) <= self.width or 0 <= (self.point3[1] + self.yy2) <= self.height or
               self.fs2_n_line == True):
            self.points2.append((self.point3[0] + self.xx2, self.point3[1] + self.yy2))
            self.xx2 += self.tx2
            self.yy2 += self.ty2
            if self.fs2_n_line == True:
                continue
        if self.fs2_n_line == False:
            self.xx2 -= self.tx2
            self.yy2 -= self.ty2
        self.fs2_n_line = False

