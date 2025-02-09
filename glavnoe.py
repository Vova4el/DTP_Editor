def triangle_area(x1, y1, x2, y2, x3, y3):
    return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0


def is_point_in_quad(px, py, x1, y1, x2, y2, x3, y3, x4, y4):
    # Площадь четырёхугольника (сумма площадей двух треугольников)
    quad_area = triangle_area(x1, y1, x2, y2, x3, y3) + triangle_area(x1, y1, x3, y3, x4, y4)

    # Площадь треугольников, образованных точкой и сторонами четырёхугольника
    area1 = triangle_area(px, py, x1, y1, x2, y2)
    area2 = triangle_area(px, py, x2, y2, x3, y3)
    area3 = triangle_area(px, py, x3, y3, x4, y4)
    area4 = triangle_area(px, py, x4, y4, x1, y1)

    # Сумма площадей треугольников
    total_area = area1 + area2 + area3 + area4

    # Если сумма площадей треугольников равна площади четырёхугольника, точка внутри
    return abs(total_area - quad_area) < 1e-9


# Пример использования
px, py = 150, 247  # Координаты точки
x1, y1 = 33, 43  # Координаты углов четырёхугольника
x2, y2 = 1592, 48
x3, y3 = 1573, 685
x4, y4 = 48, 752

if is_point_in_quad(px, py, x1, y1, x2, y2, x3, y3, x4, y4):
    print("Точка находится внутри четырёхугольника")
else:
    print("Точка находится вне четырёхугольника")
