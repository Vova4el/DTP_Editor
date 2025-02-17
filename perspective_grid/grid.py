from tkinter import Label, Frame

import cv2
import math
import numpy as np
from parallel_and_intersection.parallel import Parallel

import math

class Grid:

    def __init__(self):
        self.points = []
        self.points_distance = []
        self.s = None
        self.s2 = None
        self.selected_point_index = None
        self.f = False
        self.mint = []
        self.allPoints = []
        self.w = None
        self.h = None
        self.img_width= 0
        self.img_height = 0
        self.height = None
        self.width = None
        self.main_point_left_up = None
        self.sizeWH = [1, 1, 1, 1]
        self.jmin = 0
        self.jmax = 0
        self.imin = 0
        self.imax = 0

        self.points_in_new_img = []

    def make_grid(self):
        if len(self.points) == 4 and self.f == False and self.selected_point_index is None:
            self.allPoints = []
            self.s = None
            self.s2 = None
            self.f = True
            self.mint = []
            fs1 = True
            fs2 = True
            s_p_1, s_p_2 = [], []
            s_p2_1, s_p2_2 = [], []
            line1 = (
            self.points[0][0], self.points[0][1], self.points[2][0], self.points[2][1])  # координаты первой линии
            line2 = (self.points[1][0], self.points[1][1], self.points[3][0], self.points[3][1])
            center = self.find_intersection(line1, line2)
            self.mint.append([self.points[0], self.points[3], self.points[1], self.points[2]])
            self.mint.append([self.points[3], self.points[2], self.points[0], self.points[1]])
            result = self.check_lines_intersection(self.mint[0][0], self.mint[0][1], self.mint[0][2], self.mint[0][3])

            if result == "Прямые параллельны или совпадают":
                s_p_1, s_p_2 = self.div_S_paral(self.mint[0])
                for i in range(len(s_p_1)):
                    s_p_1[i] = [s_p_1[i][1], s_p_1[i][0]]
                for i in range(len(s_p_2)):
                    s_p_2[i] = [s_p_2[i][1], s_p_2[i][0]]

            else:
                fs1 = False
                self.s = self.find_new_point(self.mint[0][0], self.mint[0][1], self.mint[0][2], self.mint[0][3])
            result = self.check_lines_intersection(self.mint[1][0], self.mint[1][1], self.mint[1][2], self.mint[1][3])
            if result == "Прямые параллельны или совпадают":
                s_p2_1, s_p2_2 = self.div_S_paral(self.mint[1])
            else:
                fs2 = False
                self.s2 = self.find_new_point(self.mint[1][0], self.mint[1][1], self.mint[1][2], self.mint[1][3])

            if fs1 == False:
                s_p_1, self.sizeWH[0], s_p_2, self.sizeWH[1] = self.div_S_peresek(self.mint[0], self.s, center, self.s2)
                self.imax = len(s_p_1)+len(s_p_2)
            if fs2 == False:
                s_p2_1, self.sizeWH[2], s_p2_2, self.sizeWH[3] = self.div_S_peresek(self.mint[1], self.s2, center,
                                                                                    self.s)
                for i in range(len(s_p2_1)):
                    s_p2_1[i] = [s_p2_1[i][1], s_p2_1[i][0]]
                for i in range(len(s_p2_2)):
                    s_p2_2[i] = [s_p2_2[i][1], s_p2_2[i][0]]
            self.allPoints = np.empty((len(s_p_1) + len(s_p_2) + 2, len(s_p2_1) + len(s_p2_2) + 2), dtype=object)
            # self.check_side(s_p_1, s_p_2, s_p2_1, s_p2_2)
            self.process_points(s_p_1, s_p_2, s_p2_1, s_p2_2)

    def check_side(self, s_p_1, s_p_2, s_p2_1, s_p2_2):
        for i in range(len(s_p_1) - 1, -1, -1):
            arr = [s_p_1[i][1], s_p_1[i][0]]
            for j in range(len(s_p2_1) - 1, -1, -1):
                t = self.find_new_point(s_p_1[i][0], s_p_1[i][1], s_p2_1[j][0], s_p2_1[j][1])
                arr.append(t)
                f = self.are_points_in_same_direction(arr[0], arr[1], arr[2])
                arr.pop(0)
        for i in range(len(s_p_1) - 1, -1, -1):
            arr = [s_p_1[i][0], s_p_1[i][1]]
            for j in range(len(s_p2_2)):
                t = self.find_new_point(s_p_1[i][0], s_p_1[i][1], s_p2_2[j][0], s_p2_2[j][1])
                arr.append(t)
                f = self.are_points_in_same_direction(arr[0], arr[1], arr[2])
                arr.pop(0)
        for i in range(len(s_p_2)):
            arr = [s_p_2[i][1], s_p_2[i][0]]
            for j in range(len(s_p2_1) - 1, -1, -1):
                t = self.find_new_point(s_p_2[i][0], s_p_2[i][1], s_p2_1[j][0], s_p2_1[j][1])
                arr.append(t)
                f = self.are_points_in_same_direction(arr[0], arr[1], arr[2])
                arr.pop(0)
        for i in range(len(s_p_2)):
            arr = [s_p_2[i][0], s_p_2[i][1]]
            for j in range(len(s_p2_2)):
                t = self.find_new_point(s_p_2[i][0], s_p_2[i][1], s_p2_2[j][0], s_p2_2[j][1])
                arr.append(t)
                f = self.are_points_in_same_direction(arr[0], arr[1], arr[2])
                arr.pop(0)

    def process_points(self, s_p_1, s_p_2, s_p2_1, s_p2_2):
        # Вспомогательная функция для обработки строк
        def process_rows(start_row, s_p, s_p2_1, s_p2_2):
            for i in range(len(s_p)):
                for j in range(len(s_p2_1)):
                    t = self.find_new_point(s_p[i][0], s_p[i][1], s_p2_1[j][0], s_p2_1[j][1])
                    self.allPoints[start_row + i][j] = t
                self.allPoints[start_row + i][len(s_p2_1)] = s_p[i][0]
                self.allPoints[start_row + i][len(s_p2_1) + 1] = s_p[i][1]
                for j in range(len(s_p2_2)):
                    t = self.find_new_point(s_p[i][0], s_p[i][1], s_p2_2[j][0], s_p2_2[j][1])
                    self.allPoints[start_row + i][j + len(s_p2_1) + 2] = t

        # Вспомогательная функция для обработки столбцов
        def process_columns(start_row, s_p2_1, s_p2_2):
            for j in range(len(s_p2_1)):
                self.allPoints[start_row][j] = s_p2_1[j][0]
            self.allPoints[start_row][len(s_p2_1)] = self.points[0]
            self.allPoints[start_row][len(s_p2_1) + 1] = self.points[1]
            for j in range(len(s_p2_2)):
                self.allPoints[start_row][len(s_p2_1) + 2 + j] = s_p2_2[j][0]

            for j in range(len(s_p2_1)):
                self.allPoints[start_row + 1][j] = s_p2_1[j][1]
            self.allPoints[start_row + 1][len(s_p2_1)] = self.points[3]
            self.allPoints[start_row + 1][len(s_p2_1) + 1] = self.points[2]
            for j in range(len(s_p2_2)):
                self.allPoints[start_row + 1][len(s_p2_1) + 2 + j] = s_p2_2[j][1]

        # Обработка строк для s_p_1
        process_rows(0, s_p_1, s_p2_1, s_p2_2)
        # Обработка столбцов
        process_columns(len(s_p_1), s_p2_1, s_p2_2)

        # Обработка строк для s_p_2
        process_rows(len(s_p_1) + 2, s_p_2, s_p2_1, s_p2_2)

    def Distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def line_intersects_segment(self, A, B, C, x1, y1, x2, y2):
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

    def div_S_peresek(self, mint, s, center, s2):
        lUp = mint[0]
        lDown = mint[1]
        rUp = mint[2]
        rDown = mint[3]
        s_l, sizewh = self.get_line_s(lUp, rUp, lDown, rDown, center, s, s2)
        s_p = []
        for i in range(len(s_l)):
            # s_p.append(s_l[N - 1 - i])
            s_p.append(s_l[len(s_l) - 1 - i])
        s_l2, sizewh2 = self.get_line_s(lDown, rDown, lUp, rUp, center, s, s2)
        return s_p, sizewh, s_l2, sizewh2

    def div_S_paral(self, mint):
        points1S, points4S = self.get_lines_s_parallel(mint[0], mint[1], mint[2], mint[3])
        points2S, points3S = self.get_lines_s_parallel(mint[1], mint[0], mint[3], mint[2])

        s_l = []
        s_l2 = []
        s_p = []
        for i in range(len(points4S)):
            s_l2.append([points4S[i], points1S[i]])
        for i in range(len(points3S)):
            s_l.append([points3S[i], points2S[i]])
        for i in range(len(s_l2)):
            s_p.append(s_l2[len(s_l2) - 1 - i])
        return s_p, s_l

    def check_intersection(self, P1, P2, S1, S2):
        # Распаковка координат точек прямой
        x1, y1 = P1
        x2, y2 = P2

        # Распаковка координат точек отрезка
        x3, y3 = S1
        x4, y4 = S2

        # Коэффициенты уравнения прямой
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2

        # Параметры отрезка
        dx = x4 - x3
        dy = y4 - y3

        denominator = A * dx + B * dy

        if denominator == 0:
            # Прямая и отрезок параллельны
            return False

        t = -(A * x3 + B * y3 + C) / denominator

        if 0 <= t <= 1:
            # Точка пересечения
            intersection_x = x3 + t * dx
            intersection_y = y3 + t * dy
            return True, (intersection_x, intersection_y)

        return False

    # отображает удалённость от концов отрезка точки в %
    def point_position_in_percentages(self, A, B, P):
        # Координаты начального отрезка
        x1, y1 = A
        x2, y2 = B

        # Координаты заданной точки
        xp, yp = P

        # Вычисление длины отрезка AB
        segment_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # Вычисление расстояния от точки A до точки P
        distance_AP = np.sqrt((xp - x1) ** 2 + (yp - y1) ** 2)

        # Вычисление расстояния от точки B до точки P
        distance_BP = np.sqrt((xp - x2) ** 2 + (yp - y2) ** 2)

        # Вычисление положения точки P в процентах от точек A и B
        percentage_from_A = (distance_AP / segment_length) * 100
        percentage_from_B = (distance_BP / segment_length) * 100

        return percentage_from_A, percentage_from_B

    # деление отрезка на равные части
    def divide_segment(self, A, B, N):
        x1, y1 = A
        x2, y2 = B

        delta_x = (x2 - x1) / N
        delta_y = (y2 - y1) / N

        points = []
        for i in range(N + 1):
            x = x1 + i * delta_x
            y = y1 + i * delta_y
            points.append((x, y))

        return points

    # строит паралельный отрезок на заланной точке
    def find_parallel_segment(self, A, B, P):
        # Координаты начального отрезка
        x1, y1 = A
        x2, y2 = B

        # Координаты точки, через которую должен пройти новый отрезок
        xp, yp = P

        # Вычисление изменений координат отрезка AB
        dx = x2 - x1
        dy = y2 - y1

        # Вычисление координат новых конечных точек
        xA_prime = xp + dx
        yA_prime = yp + dy
        xB_prime = xp - dx
        yB_prime = yp - dy

        A_prime = (xA_prime, yA_prime)
        B_prime = (xB_prime, yB_prime)

        return A_prime, B_prime

    # строит равноудолённые точки на прямой
    def get_lines_s_parallel(self, point1, point2, point3, point4):
        xx = point1[0] - point2[0]
        yy = point1[1] - point2[1]
        tx = xx
        ty = yy
        xx2 = point3[0] - point4[0]
        yy2 = point3[1] - point4[1]
        tx2 = xx2
        ty2 = yy2
        pointsS1 = []
        pointsS2 = []
        f = True
        while f == True:
            f = False
            f = (self.does_line_intersect_square((point1[0] + xx, point1[1] + yy), (point3[0] + xx2, point3[1] + yy2),
                                                 [(0, 0), (0, self.height), (self.width, self.height), (self.width, 0)])
                 and self.Distance((point1[0] + xx, point1[1] + yy), (point3[0] + xx2, point3[1] + yy2)) < 1000)
            pointsS1.append((point1[0] + xx, point1[1] + yy))
            xx += tx
            yy += ty
            pointsS2.append((point3[0] + xx2, point3[1] + yy2))
            xx2 += tx2
            yy2 += ty2
        return pointsS1, pointsS2

    # проверяет, параллельны ли прямые или пересекаются
    def check_lines_intersection(self, p1, p2, p3, p4):
        # Функция для нахождения определителя
        def determinant(a, b, c, d):
            return a * d - b * c

        # Координаты точек
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        # Векторы направлений
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x4 - x3
        dy2 = y4 - y3

        # Вычисляем определитель
        det = determinant(dx1, dy1, dx2, dy2)
        if det < 0.0001 and det > -0.0001:
            return "Прямые параллельны или совпадают"
        else:
            return "Прямые пересекаются"

    def is_line_segment_intersect(self, P1, P2, S1, S2):
        # Распаковка координат точек прямой
        x1, y1 = P1
        x2, y2 = P2

        # Распаковка координат точек отрезка
        x3, y3 = S1
        x4, y4 = S2

        # Коэффициенты уравнения прямой
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2
        # Вычисляем значения функции для концов отрезка
        f1 = A * x3 + B * y3 + C
        f2 = A * x4 + B * y4 + C

        # Если произведение f1 и f2 меньше или равно нулю, то отрезок пересекает прямую
        return f1 * f2 <= 0

    #  строит точки относительно точки схода
    def get_line_s(self, lUp, rUp, lDown, rDown, center, s, s2):
        sizeWH = 1
        t = []
        origLDist = (self.Distance(lUp,lDown) / 100)*5
        origRDist = (self.Distance(rUp,rDown) / 100)*5
        center_line = self.find_new_point(lUp, rUp, center, s)
        f = True
        fDist = True
        while f == True:
            f = False
            t1 = self.find_new_point(center_line, rDown, lUp, lDown)
            t2 = self.find_new_point(center_line, lDown, rUp, rDown)
            fDist = self.Distance(rUp,rDown) >= origRDist or self.Distance(lUp,lDown)>=origLDist
            if (self.does_line_intersect_square(t1, t2, [(0, 0), (0, self.height), (self.width, self.height),
                                                         (self.width, 0)]) == False
                    and self.are_points_in_same_direction(lDown, lUp, t1)
                and self.are_points_in_same_direction(rDown, rUp, t2)) and fDist==True:

                lDown = lUp
                rDown = rUp
                rUp = t2
                lUp = t1
                center = self.find_new_point(rDown, lUp, rUp, lDown)
                center_line = self.find_new_point(lUp, rUp, center, s)
                k = 0
                sizet = sizeWH
                sizeWHt = sizeWH
                fk = False
                while (k <= 10):
                    if s2 != None:
                        tl = self.find_new_point(center, s2, lUp, lDown)
                        tr = self.find_new_point(center, s2, rUp, rDown)
                    else:
                        center2 = self.find_parallel_segment(lDown, rDown, center)
                        tl = self.find_new_point(center2[0], center2[1], lUp, lDown)
                        tr = self.find_new_point(center2[0], center2[1], rUp, rDown)
                    sizet = sizet / 2
                    sizeWHt = sizeWHt - sizet
                    if self.does_line_intersect_square(tl, tr, [(0, 0), (0, self.height), (self.width, self.height),
                                                                (self.width, 0)]) == False:
                        lUp = tl
                        rUp = tr
                    else:
                        sizeWHt = sizeWHt + sizet
                        fk = True
                        lDown = tl
                        rDown = tr
                        sizeWH = sizeWHt
                    center = self.find_new_point(rDown, lUp, rUp, lDown)
                    center_line = self.find_new_point(lUp, rUp, center, s)
                    k += 1
                if fk == False:
                    sizeWH = 1
                t2 = rUp
                t1 = lUp
                t.append([t1, t2])
                continue
            f = self.are_points_in_same_direction(lDown, lUp, t1) and self.are_points_in_same_direction(rDown, rUp, t2)
            f2 = f
            if self.Distance(s, t1) <= 20 and self.Distance(s, t2) <= 20:
                f = False

            if f == True:
                lDown = lUp
                rDown = rUp
                rUp = t2
                lUp = t1
                center_line = self.find_new_point(t1, t2, center, s)
                t.append([t1, t2])
            if f2 == False:
                print('f2')
                sizeWH = 1
                sizet = 1
                while (self.are_points_in_same_direction(lDown, lUp, t1) == False
                       or self.are_points_in_same_direction(rDown, rUp, t2) == False):
                    center = self.find_new_point(rDown, lUp, rUp, lDown)
                    if s2 != None:
                        lDown = self.find_new_point(center, s2, lUp, lDown)
                        rDown = self.find_new_point(center, s2, rUp, rDown)
                    else:
                        center2 = self.find_parallel_segment(lDown, rDown, center)
                        lDown = self.find_new_point(center2[0], center2[1], lUp, lDown)
                        rDown = self.find_new_point(center2[0], center2[1], rUp, rDown)
                    center = self.find_new_point(rDown, lUp, rUp, lDown)
                    center_line = self.find_new_point(lUp, rUp, center, s)
                    sizet = sizet / 2
                    t1 = self.find_new_point(center_line, rDown, lUp, lDown)
                    t2 = self.find_new_point(center_line, lDown, rUp, rDown)
                if rUp != t2:
                    lDown = lUp
                    rDown = rUp
                    rUp = t2
                    lUp = t1
                    center = self.find_new_point(rDown, lUp, rUp, lDown)
                    center_line = self.find_new_point(lUp, rUp, center, s)
                lDist = self.Distance(lUp, lDown)
                rDist = self.Distance(rUp, rDown)
                tl = lUp
                tr = rUp
                sizeWH = sizeWH - sizet
                while (self.does_line_intersect_square(tl, tr, [(0, 0), (0, self.height), (self.width, self.height),
                                                                (self.width, 0)]) == True
                       and (lDist > 5 or rDist > 5)):

                    if s2 != None:
                        lDown = self.find_new_point(center, s2, lUp, lDown)
                        rDown = self.find_new_point(center, s2, rUp, rDown)
                    else:
                        center2 = self.find_parallel_segment(lDown, rDown, center)
                        lDown = self.find_new_point(center2[0], center2[1], lUp, lDown)
                        rDown = self.find_new_point(center2[0], center2[1], rUp, rDown)
                    center = self.find_new_point(rDown, lUp, rUp, lDown)
                    center_line = self.find_new_point(lUp, rUp, center, s)
                    tl = self.find_new_point(center_line, rDown, lUp, lDown)
                    tr = self.find_new_point(center_line, lDown, rUp, rDown)
                    sizet = sizet / 2
                    if self.are_points_in_same_direction(lDown, lUp, tl) == True or self.are_points_in_same_direction(
                            rDown, rUp, tr) == True:
                        t1 = tl
                        t2 = tr
                        lDown = lUp
                        rDown = rUp
                        rUp = t2
                        lUp = t1
                        center = self.find_new_point(rDown, lUp, rUp, lDown)
                        center_line = self.find_new_point(lUp, rUp, center, s)
                        sizeWH = sizeWH + sizet
                    lDist = self.Distance(lUp, lDown)
                    rDist = self.Distance(rUp, rDown)

                if rUp != t2:
                    lDown = lUp
                    rDown = rUp
                    rUp = t2
                    lUp = t1
                center = self.find_new_point(rDown, lUp, rUp, lDown)
                center_line = self.find_new_point(lUp, rUp, center, s)
                k = 0
                sizeWHt = sizeWH
                tl = lUp
                tr = rUp
                fk= False
                while (k < 10):
                    if s2 != None:
                        tl = self.find_new_point(center, s2, lUp, lDown)
                        tr = self.find_new_point(center, s2, rUp, rDown)
                    else:
                        center2 = self.find_parallel_segment(lDown, rDown, center)
                        tl = self.find_new_point(center2[0], center2[1], lUp, lDown)
                        tr = self.find_new_point(center2[0], center2[1], rUp, rDown)
                    sizet = sizet / 2
                    sizeWHt = sizeWHt - sizet
                    if self.does_line_intersect_square(tl, tr, [(0, 0), (0, self.height), (self.width, self.height),
                                                                (self.width, 0)]) == False:
                        lUp = tl
                        rUp = tr

                    else:
                        sizeWHt = sizeWHt + sizet
                        fk = True
                        lDown = tl
                        rDown = tr
                        sizeWH = sizeWHt
                    center = self.find_new_point(rDown, lUp, rUp, lDown)
                    center_line = self.find_new_point(lUp, rUp, center, s)

                    k += 1
                t2 = rUp
                t1 = lUp
                t.append([t1, t2])
            if f2 == True and fDist == False:
                f = fDist
        return t, sizeWH

    # выводит точку пересечения
    def find_new_point(self, point1, point2, point3, point4):
        line1 = (point1[0], point1[1], point2[0], point2[1])  # координаты первой линии
        line2 = (point3[0], point3[1], point4[0], point4[1])
        t = self.find_intersection(line1, line2)
        return t

    # выводит точку пересечения
    def find_intersection(self, line1, line2):
        # Каждая линия задается двумя точками в формате (x1, y1, x2, y2)
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2

        # Проверяем, является ли первая прямая вертикальной
        if x2 - x1 == 0:
            k1 = float('inf')  # Задаем наклон как бесконечность для вертикальной прямой
            b1 = x1  # b1 в этом случае - это x1, так как x постоянно
        else:
            k1 = (y2 - y1) / (x2 - x1)
            b1 = y1 - k1 * x1

        # Проверяем, является ли вторая прямая вертикальной
        if x4 - x3 == 0:
            k2 = float('inf')  # Задаем наклон как бесконечность для вертикальной прямой
            b2 = x3  # b2 в этом случае - это x3
        else:
            k2 = (y4 - y3) / (x4 - x3)
            b2 = y3 - k2 * x3

        # Если обе прямые вертикальны, то они либо параллельны, либо совпадают
        if k1 == float('inf') and k2 == float('inf'):
            if b1 == b2:
                return None  # Совпадающие вертикальные прямые (возможно, один и тот же отрезок)
            else:
                return None  # Параллельные вертикальные прямые

        # Если первая прямая вертикальна, находим точку пересечения с использованием уравнения второй прямой
        if k1 == float('inf'):
            x_intersect = b1
            y_intersect = k2 * x_intersect + b2
            return (x_intersect, y_intersect)

        # Если вторая прямая вертикальна, находим точку пересечения с использованием уравнения первой прямой
        if k2 == float('inf'):
            x_intersect = b2
            y_intersect = k1 * x_intersect + b1
            return (x_intersect, y_intersect)

        # Если прямые параллельны (коэффициенты наклона равны), то пересечения нет
        if k1 == k2:
            return None  # Прямые параллельны
        # Находим точку пересечения для обычных наклонов
        x_intersect = (b2 - b1) / (k1 - k2)
        y_intersect = k1 * x_intersect + b1

        return (x_intersect, y_intersect)

    # выводит точку пересечения
    def find_vanishing_point(self, point1, point2, point3, point4):
        # Пример линий
        line1 = (point1[0], point1[1], point2[0], point2[1])  # координаты первой линии
        line2 = (point3[0], point3[1], point4[0], point4[1])  # координаты второй линии

        # Нахождение точки схода
        vanishing_point = self.find_intersection(line1, line2)
        return vanishing_point

    def are_points_in_same_direction(self, A, B, C):
        x1, y1 = A
        x2, y2 = B
        x3, y3 = C

        # Вектор AB
        vector1 = (x2 - x1, y2 - y1)

        # Вектор BC
        vector2 = (x3 - x2, y3 - y2)

        # Нормализуем векторы (это дает их направление)
        norm1 = np.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
        norm2 = np.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

        unit_vector1 = (vector1[0] / norm1, vector1[1] / norm1)

        unit_vector2 = (vector2[0] / norm2, vector2[1] / norm2)

        # Находим косинус угла между векторами
        dot_product = unit_vector1[0] * unit_vector2[0] + unit_vector1[1] * unit_vector2[1]

        # Если косинус угла равен 1 или близок к 1, то векторы идут в одном направлении
        return dot_product >= 0.999

    def triangle_area(self, x1, y1, x2, y2, x3, y3):
        return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0

    def is_point_in_quad(self,px, py, x1, y1, x2, y2, x3, y3, x4, y4):
        # Площадь четырёхугольника (сумма площадей двух треугольников)
        quad_area = self.triangle_area(x1, y1, x2, y2, x3, y3) + self.triangle_area(x1, y1, x3, y3, x4, y4)

        # Площадь треугольников, образованных точкой и сторонами четырёхугольника
        area1 = self.triangle_area(px, py, x1, y1, x2, y2)
        area2 = self.triangle_area(px, py, x2, y2, x3, y3)
        area3 = self.triangle_area(px, py, x3, y3, x4, y4)
        area4 = self.triangle_area(px, py, x4, y4, x1, y1)

        # Сумма площадей треугольников
        total_area = area1 + area2 + area3 + area4

        # Если сумма площадей треугольников равна площади четырёхугольника, точка внутри
        return abs(total_area - quad_area) < 1e-9

    def check_point_in_blocks(self, point, all_blocks):
        for blocks in all_blocks:
            for block in blocks:
                p_b = []
                for p in block:
                    p_b.append(self.allPoints[p[0]][p[1]])
                if self.is_point_in_quad(point[0], point[1], p_b[0][0], p_b[0][1], p_b[1][0], p_b[1][1], p_b[3][0], p_b[3][1], p_b[2][0], p_b[2][1]):
                    return True
        return False

    def get_dist(self, all_blocks,image, parent_frame):
        p_d = []
        for point in self.points_distance:
            p_d.append(self.get_point_2D(all_blocks,point))
            if len(p_d) == 2:
                dist = self.Distance(p_d[0], p_d[1])
                self.labelDist = Label(parent_frame, text="Дистанция = "+str(round(dist * (int(self.h) / (int(self.h) * 2)), 2))+"cм")
                self.labelDist.grid(row=9, column=0, padx=0, pady=0, sticky='w')
                image.create_line_dist(p_d[0],p_d[1])
    def get_point_2D(self, all_blocks,point):
        true_block, new_img_points = None, None
        for i, blocks in enumerate(all_blocks):
            for block in blocks:
                p_b = [self.allPoints[p[0]][p[1]] for p in block]

                if self.is_point_in_quad(point[0], point[1], p_b[0][0], p_b[0][1], p_b[1][0], p_b[1][1], p_b[3][0], p_b[3][1], p_b[2][0], p_b[2][1]):
                    new_img_points = [p_b[0], p_b[1], p_b[3], p_b[2]]
                    true_block = [block,i]
                    break
            if true_block:
                break
        if true_block:
            if self.s2 is not None and self.s is not None:
                mint2 = []
                mint2.append([new_img_points[0], new_img_points[3], new_img_points[1], new_img_points[2]])
                mint2.append([new_img_points[3], new_img_points[2], new_img_points[0], new_img_points[1]])
                p1, p2 = self.find_parallel_segment(self.s, self.s2, new_img_points[0])
                s1p1 = self.find_new_point(mint2[0][0], mint2[0][1], p1, p2)
                s1p2 = self.find_new_point(mint2[0][2], mint2[0][3], p1, p2)
                ts1 = self.find_new_point(s1p1, s1p2, point, self.s)

                s2p1 = self.find_new_point(mint2[1][0], mint2[1][1], p1, p2)
                s2p2 = self.find_new_point(mint2[1][2], mint2[1][3], p1, p2)
                ts2 = self.find_new_point(s2p1, s2p2, point, self.s2)

                a = self.point_position_in_percentages(s1p1, s1p2, ts1)
                if true_block[0][0][1] == self.jmin:
                    a = ((a[0] / 100) *(int(self.w) * 2 * self.sizeWH[2]))
                elif true_block[0][0][1] == self.jmax:
                    a = (int(self.w) * 2 * self.sizeWH[2]) + ((a[0] / 100) *(int(self.w) * 2 * self.sizeWH[3]))
                    for i in range(self.jmax-1):
                        a = a + (int(self.w) * 2)
                else:
                    tminus = self.jmin
                    a = ((a[0] / 100) * (int(self.w) * 2))
                    if self.jmin == 0:
                        tminus += 1
                        a = a+ (int(self.w) * 2 * self.sizeWH[2])
                    for i in range(true_block[0][0][1]-tminus):
                        a = a + (int(self.w) * 2)
                print('ssssssssssssss')
                print(true_block)
                print(len(self.allPoints)-1)
                print(len(all_blocks) - 1)
                print(true_block[0][0][0])
                print(len(all_blocks) - 2)
                a2 = self.point_position_in_percentages(s2p1, s2p2, ts2)
                if true_block[1] == 0:
                    a2 = ((a2[1] / 100) *(int(self.h) * 2 * self.sizeWH[0]))
                elif true_block[0][0][0] == (len(self.allPoints) -2) :
                    print( self.sizeWH[1])
                    a2 = (int(self.h) * 2 * self.sizeWH[0]) + ((a2[1] / 100) *(int(self.h) * 2 * self.sizeWH[1]))
                    for i in range(len(all_blocks)-2):
                        a2 = a2 + (int(self.h) * 2)
                else:
                    tminus = 0
                    a2 = ((a2[1] / 100) * (int(self.h) * 2))
                    if self.imin == 0:
                        tminus += 1
                        a2 = a2 + (int(self.h) * 2 * self.sizeWH[0])

                    for i in range(true_block[1]-tminus):
                        a2 = a2 + (int(self.h) * 2)

                return [a, a2]

            else:
                peresek = []
                par1_1 = [new_img_points[0], 0]
                par1_2 = [new_img_points[1], 1]
                par2_1 = [new_img_points[3], 3]
                par2_2 = [new_img_points[2], 2]
                result = self.check_lines_intersection(par1_1[0], par1_2[0], par2_1[0], par2_2[0])
                if result == "Прямые пересекаются":
                    par1_1 = [new_img_points[0], 0]
                    par1_2 = [new_img_points[3], 3]
                    par2_1 = [new_img_points[1], 1]
                    par2_2 = [new_img_points[2], 2]
                if self.check_intersection(par1_1[0], point, par2_1[0], par2_2[0]):
                    p = self.find_new_point(par1_1[0], point, par2_1[0], par2_2[0])
                    peresek.append([par1_1, p, par2_1, par2_2])
                if self.check_intersection(par1_2[0], point, par2_1[0], par2_2[0]):
                    p = self.find_new_point(par1_2[0], point, par2_1[0], par2_2[0])
                    peresek.append([par1_2, p, par2_1, par2_2])
                if self.check_intersection(par2_1[0], point, par1_1[0], par1_2[0]):
                    p = self.find_new_point(par2_1[0], point, par1_1[0], par1_2[0])
                    peresek.append([par2_1, p, par1_1, par1_2])
                if self.check_intersection(par2_2[0], point, par1_1[0], par1_2[0]):
                    p = self.find_new_point(par2_2[0], point, par1_1[0], par1_2[0])
                    peresek.append([par2_2, p, par1_1, par1_2])
                p = []
                for per in peresek:
                    a = self.point_position_in_percentages(per[2][0], per[3][0], per[1])
                    if per[2][1] == 0 and per[3][1] == 3 or per[2][1] == 1 and per[3][1] == 2:
                        y = (a[0] / 100) * (int(self.h) * 2)
                        if per[2][1] == 0:
                            t = [0, y]
                        else:
                            t = [(int(self.w) * 2), y]
                        p.append([per[0][1], t])
                    else:
                        x = (a[0] / 100) * (int(self.w) * 2)
                        if per[2][1] == 0:
                            t = [x, 0]
                        else:
                            t = [x, (int(self.h) * 2)]
                        p.append([per[0][1], t])
                ugly = [[0, 0], [(int(self.w) * 2), 0], [(int(self.w) * 2), (int(self.h) * 2)], [0, (int(self.h) * 2)]]
                new_point = self.find_new_point(ugly[p[0][0]], p[0][1], ugly[p[1][0]], p[1][1])

                a = new_point[0]
                if true_block[0][0][1] == self.jmin:
                    a = a * self.sizeWH[2]
                elif true_block[0][0][1] == self.jmax:
                    a = (int(self.w) * 2 * self.sizeWH[2]) + (a * self.sizeWH[3])
                    for i in range(self.jmax-self.jmin-1):
                        a = a + (int(self.w) * 2)
                else:
                    a = a+ (int(self.w) * 2 * self.sizeWH[2])
                    for i in range(true_block[0][0][1]-self.jmin-1):
                        a = a + (int(self.w) * 2)


                a2 = new_point[1]
                if true_block[1] == 0:
                    a2 = (a2 * self.sizeWH[0])
                elif true_block[0][0][0] == (len(self.allPoints) -2):
                    a2 = (int(self.h) * 2 * self.sizeWH[0]) + (a2 * self.sizeWH[1])
                    for i in range(len(all_blocks)-2):
                        a2 = a2 + (int(self.h) * 2)
                else:
                    print(3333)
                    a2 = a2 + (int(self.h) * 2 * self.sizeWH[0])
                    for i in range(true_block[1]-1):
                        a2 = a2 + (int(self.h) * 2)
                return [a, a2]
        else:
            return False

