def add_lines_frame(self):
    if len(self.grid.allPoints) > 0:

        self.all_blocks = []
        self.image = self.original_image.copy()
        draw = ImageDraw.Draw(self.image)
        jmin = len(self.grid.allPoints[0])
        jmax = 0
        for i in range(len(self.grid.allPoints) - 1):
            arr = []
            for j in range(len(self.grid.allPoints[0]) - 1):
                if (0 <= self.grid.allPoints[i][j][0] <= self.grid.width and
                    0 <= self.grid.allPoints[i][j][1] <= self.grid.height) or (
                        0 <= self.grid.allPoints[i][j + 1][0] <= self.grid.width and
                        0 <= self.grid.allPoints[i][j + 1][1] <= self.grid.height) or (
                        0 <= self.grid.allPoints[i + 1][j][0] <= self.grid.width and
                        0 <= self.grid.allPoints[i + 1][j][1] <= self.grid.height) or (
                        0 <= self.grid.allPoints[i + 1][j + 1][0] <= self.grid.width and
                        0 <= self.grid.allPoints[i + 1][j + 1][1] <= self.grid.height):
                    arr.append([(i, j), (i, j + 1), (i + 1, j), (i + 1, j + 1)])
                    if jmin > j:
                        jmin = j
                    if jmax < j:
                        jmax = j
                    # Координаты четырех линий ячейки
                    lines = [
                        (self.grid.allPoints[i][j][0], self.grid.allPoints[i][j][1],
                         self.grid.allPoints[i + 1][j][0], self.grid.allPoints[i + 1][j][1]),

                        (self.grid.allPoints[i][j][0], self.grid.allPoints[i][j][1],
                         self.grid.allPoints[i][j + 1][0], self.grid.allPoints[i][j + 1][1]),

                        (self.grid.allPoints[i + 1][j + 1][0], self.grid.allPoints[i + 1][j + 1][1],
                         self.grid.allPoints[i][j + 1][0], self.grid.allPoints[i][j + 1][1]),

                        (self.grid.allPoints[i + 1][j + 1][0], self.grid.allPoints[i + 1][j + 1][1],
                         self.grid.allPoints[i + 1][j][0], self.grid.allPoints[i + 1][j][1])
                    ]

                    # Рисуем линии
                    for line in lines:
                        draw.line(line, fill="green", width=2)

            if arr != []:
                self.all_blocks.append(arr)