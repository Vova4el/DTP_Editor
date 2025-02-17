from random import random
from tkinter import Frame, Label, Entry, Button, messagebox, END, Canvas

from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance, ImageDraw
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageTk

from Dialog.input_dialog import InputDialog
from ai.ai import AI
from image_edit import ImageEdit
from image_info import ImageInfo
from perspective_grid.grid import Grid

class Event:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class ImageGrid(ImageInfo):
    def __init__(self, image, path, tab):
        super().__init__(image, path, tab)
        # Additional attributes for ImageGrid
        self.grid = Grid()  # Initialize or adjust as needed
        self.ai = AI()

        self.main_points_id = []
        self.points_distance = []
        self.line_distance_ids_BR= []
        self.root = None
        self.right_frame = None  # Or replace with actual initialization
        self.additional_frame = None  # Атрибут для хранения дополнительного фрейма

        self.line_ids_BR= []

        self.img_height = None
        self.img_width = None
        self.zoom_level = None
        self.image_on_canvas = None
        self.canvas2 = None

        self.all_blocks = []

    def set_canvas(self, canvas):
        self.canvas = canvas
        self._bind_zoom()
        self.zoom_container = self.canvas.create_rectangle(0, 0, self.image.width, self.image.height, width=0)
        self._show_zoomed_image()

        # Привязка клика к методу рисования точки
        self.canvas.bind("<Button-3>", self._draw_point)

    def _get_actual_image_coordinates(self, event):
        # Координаты клика на Canvas
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        # Преобразуем их в координаты на изображении
        bbox = self.canvas.bbox(self.image_container)
        image_x = (canvas_x - bbox[0]) / self.imscale
        image_y = (canvas_y - bbox[1]) / self.imscale
        return int(image_x), int(image_y)

    def display_click_coordinates(self, event):
        image_x, image_y = self._get_actual_image_coordinates(event)

    def _draw_point(self, event):
        image_x, image_y = self._get_actual_image_coordinates(event)
        # Преобразование координат изображения в координаты на канвасе
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        for point in self.main_points_id:
            radius = 5 * self.imscale
            if (point["image_x"] - radius <= image_x <= point["image_x"] + radius and
                    point["image_y"] - radius <= image_y <= point["image_y"] + radius):
                return

        if len(self.grid.points) < 4:
            x,y = self._get_actual_image_coordinates(event)
            self.grid.points.append((x, y))
            radius = 5 * self.imscale  # Радиус точки
            point_id = self.canvas.create_oval(
                canvas_x - radius, canvas_y - radius,
                canvas_x + radius, canvas_y + radius,
                 outline='red', width=4
            )
            self.main_points_id.append({
                "id": point_id,
                "image_x": image_x,
                "image_y": image_y,
                "canvas_x": canvas_x,
                "canvas_y": canvas_y
            })
        if len(self.grid.points) == 4 and len(self.line_ids_BR) != 4:

            # Создайте копию оригинального изображения
            new_img = self.original_image.copy()
            draw = ImageDraw.Draw(new_img)

            # Нарисуйте линии на изображении
            draw.line([tuple(map(int, self.grid.points[0])), tuple(map(int, self.grid.points[1]))], fill=(0, 0, 255), width=6)
            draw.line([tuple(map(int, self.grid.points[1])), tuple(map(int, self.grid.points[2]))], fill=(255, 0, 0), width=6)
            draw.line([tuple(map(int, self.grid.points[2])), tuple(map(int, self.grid.points[3]))], fill=(0, 0, 255), width=6)
            draw.line([tuple(map(int, self.grid.points[3])), tuple(map(int, self.grid.points[0]))], fill=(255, 0, 0), width=6)

            # Преобразуйте список кортежей в numpy массив
            points_np = np.array(self.grid.points, dtype=np.int32)

            # Создайте маску
            mask = Image.new('L', self.original_image.size, 0)
            mask_draw = ImageDraw.Draw(mask)

            # Заполните полигон (выделенную область) белым цветом на маске
            mask_draw.polygon([tuple(map(int, pt)) for pt in self.grid.points], outline=255, fill=255)

            # Создайте новое изображение с белым фоном
            white_bg = Image.new('RGB', self.original_image.size, (255, 255, 255))

            # Примените маску к изображению, используя белый фон
            masked_image = Image.composite(new_img, white_bg, mask)

            # Найдите ограничивающий прямоугольник для выделенной области
            x, y, w, h = cv2.boundingRect(points_np)  # Это все еще нужно для расчетов
            # Вырежьте область по ограничивающему прямоугольнику
            cropped_image = masked_image.crop((x, y, x + w, y + h))
            self._unbind_grid()
            dialog = InputDialog(self.root,cropped_image)

            self.root.wait_window(dialog)
            self._bind_grid()
            self.grid.h = dialog.result[0]
            self.grid.w = dialog.result[1]
            self.add_additional_frame(self.tab)
            self._update_canvasXY()
            self.add_main_lines_frame()

    def start_grid_selection(self, root):
        self._bind_grid()
        self.root = root

    def make_grid(self):
        self.grid.height = self.image.height
        self.grid.width = self.image.width
        self.grid.f = False
        self.grid.make_grid()
        self.add_lines_frame()

    def _bind_grid(self):
        self.canvas.bind("<ButtonPress-1>", self._draw_point)
        self.canvas.bind("<B1-Motion>", self._move_point)

    def _unbind_grid(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")

        self.canvas["cursor"] = ""

    def _move_point(self, event):
        image_x, image_y = self._get_actual_image_coordinates(event)
        # Получение текущих координат курсора
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        # Проверка, если курсор находится в пределах какой-либо точки
        for i,point in enumerate(self.main_points_id):
            radius = 5 * self.imscale
            if (point["image_x"] - radius <= image_x <= point["image_x"] + radius and
                    point["image_y"] - radius <= image_y <= point["image_y"] + radius):
                self._remove_lines()
                # Обновление координат точки
                self.canvas.coords(
                    point["id"],
                    canvas_x - radius, canvas_y - radius,
                    canvas_x + radius, canvas_y + radius
                )
                # Пересчет координат на изображении
                bbox = self.canvas.bbox(self.image_container)
                # image_x = int((canvas_x - bbox[0]) / self.imscale)
                # image_y = int((canvas_y - bbox[1]) / self.imscale)
                # Обновляем координаты точки
                point["canvas_x"] = canvas_x
                point["canvas_y"] = canvas_y
                self.grid.points[i] = (image_x, image_y)
                point["image_x"] = image_x
                point["image_y"] = image_y

                self.grid.points[i] = (image_x, image_y)
                if len(self.line_ids_BR) == 4:
                    if i == 0:
                        self.entryX1.delete(0, END)
                        self.entryX1.insert(0, point["image_x"])
                        self.entryY1.delete(0, END)
                        self.entryY1.insert(0, point["image_y"])
                    elif i == 1:
                        self.entryX2.delete(0, END)
                        self.entryX2.insert(0, point["image_x"])
                        self.entryY2.delete(0, END)
                        self.entryY2.insert(0, point["image_y"])
                    elif i == 2:
                        self.entryX3.delete(0, END)
                        self.entryX3.insert(0, point["image_x"])
                        self.entryY3.delete(0, END)
                        self.entryY3.insert(0, point["image_y"])
                    elif i == 3:
                        self.entryX4.delete(0, END)
                        self.entryX4.insert(0, point["image_x"])
                        self.entryY4.delete(0, END)
                        self.entryY4.insert(0, point["image_y"])
        self._update_canvasXY()
        self.add_main_lines_frame()

    def _remove_main_points(self):
        for point_id in self.main_points_id:
            self.canvas.delete(point_id)
        self.main_points_id.clear()  # Очистка списка после удаления всех точек

    def show_entry_content(self):
        input1 = self.entry1.get()
        input2 = self.entry2.get()

        # Проверка, что оба ввода - вещественные числа
        try:
            float(input1)
            float(input2)
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите вещественные числа в оба поля.")
        else:
            result = (input1, input2)

    def _update_canvasXY(self):
        for i,point in enumerate(self.main_points_id):
            coords = self.canvas.coords(point["id"])
            radius = (coords[2] - coords[0]) / 2
            # Обновление данных точки
            point["canvas_x"] = coords[0] + radius
            point["canvas_y"] = coords[1] + radius
        if len(self.points_distance) > 0:
            for i, point in enumerate(self.points_distance):
                coords = self.canvas.coords(point["id"])
                radius = (coords[2] - coords[0]) / 2
                # Обновление данных точки
                point["canvas_x"] = coords[0] + radius
                point["canvas_y"] = coords[1] + radius
    def _update_canvas_coordinates(self):
        try:
            if self.canvas2:
                self.canvas2.destroy()
                self.canvas2 = None
            self.grid.points_distance = []  # Initialize or adjust as needed



            points = [(float(self.entryX1.get()), float(self.entryY1.get())),
                      (float(self.entryX2.get()), float(self.entryY2.get())),
                      (float(self.entryX3.get()), float(self.entryY3.get())),
                      (float(self.entryX4.get()), float(self.entryY4.get()))]
            self.grid.w = float(self.entry2.get())
            self.grid.h = float(self.entry1.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите вещественные числа во все поля.")
            return
        bbox = self.canvas.bbox(self.image_container)
        for i,point in enumerate(self.main_points_id):
            if float(point["image_x"]) != points[i][0] or float(point["image_y"]) != points[i][1]:
                self._remove_lines()

                radius = 5 * self.imscale
                canvas_x = bbox[0] + points[i][0] * self.imscale
                canvas_y = bbox[1] + points[i][1] * self.imscale
                self.canvas.coords(
                    point["id"],
                    canvas_x - radius, canvas_y - radius,
                    canvas_x + radius, canvas_y + radius
                )
                point["canvas_x"] = canvas_x
                point["canvas_y"] = canvas_y
                self.grid.points[i] = (points[i][0], points[i][1])
                point["image_x"] = points[i][0]
                point["image_y"] = points[i][1]


                self._update_canvasXY()



                self.add_main_lines_frame()
    def create_entry(self, row, column, value):
        entry = Entry(self.additional_frame)
        entry.grid(row=row, column=column, padx=0, pady=0)
        entry.insert(0, value)
        return entry

    def show_entry_content(self):
        input1 = self.entry1.get()
        input2 = self.entry2.get()

        # Проверка, что оба ввода - вещественные числа
        try:
            float(input1)
            float(input2)
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите вещественные числа в оба поля.")
        else:
            result = (input1, input2)

    def add_additional_frame(self, parent_frame):
        if self.additional_frame:
            self.additional_frame.destroy()

            # Создаем новый дополнительный фрейм
        self.additional_frame = Frame(parent_frame, bg="lightgrey")
        self.additional_frame.grid(row=0, column=1, sticky="nsew")
        self.additional_frame.grid_columnconfigure(1, weight=0)

        self.label1 = Label(self.additional_frame, text="Длина красных сторон:")
        self.label1.grid(row=1, column=0, padx=0, pady=5, sticky='w')

        self.entry1 = Entry(self.additional_frame)
        self.entry1.grid(row=1, column=1, padx=0, pady=0, sticky='w')
        self.entry1.insert(0, self.grid.h)

        self.label2 = Label(self.additional_frame, text="Длина синих сторон:")
        self.label2.grid(row=2, column=0, padx=0, pady=0, sticky='w')

        self.entry2 = Entry(self.additional_frame)
        self.entry2.grid(row=2, column=1, padx=0, pady=0, sticky='w')
        self.entry2.insert(0, self.grid.w)

        # Создаем кнопку, которая будет выводить содержимое поля ввода
        self.show_button = Button(self.additional_frame, text="Применить изменение",
                                  command=self._update_canvas_coordinates)
        self.show_button.grid(row=3, column=0, padx=(0,10), pady=10, sticky='w')

        self.labelX = Label(self.additional_frame, text="X")
        self.labelX.grid(row=3, column=1, padx=0, pady=0, sticky='w')

        self.labelY = Label(self.additional_frame, text="Y")
        self.labelY.grid(row=3, column=2, padx=0, pady=0, sticky='w')

        self.entryX1 = self.create_entry(4, 1, self.grid.points[0][0])
        self.entryY1 = self.create_entry(4, 2, self.grid.points[0][1])

        self.entryX2 = self.create_entry(5, 1, self.grid.points[1][0])
        self.entryY2 = self.create_entry(5, 2, self.grid.points[1][1])

        self.entryX3 = self.create_entry(6, 1, self.grid.points[2][0])
        self.entryY3 = self.create_entry(6, 2, self.grid.points[2][1])

        self.entryX4 = self.create_entry(7, 1, self.grid.points[3][0])
        self.entryY4 = self.create_entry(7, 2, self.grid.points[3][1])


    def remove_additional_frame(self):
        # Удаляем дополнительный фрейм, если он существует
        if self.additional_frame:
            self.additional_frame.destroy()
            self.additional_frame = None  # Очищаем ссылку после удаления

    def _remove_lines_BR(self):
        for line_id in self.line_ids_BR:
            self.canvas.delete(line_id)
        self.line_ids_BR.clear()  # Очистить список идентификаторов после удаления

    def add_main_lines_frame(self):
        if self.line_ids_BR:
            self._remove_lines_BR()
        if self.all_blocks != []:
            for point in self.points_distance:
                if "id" in point:  # Проверка на наличие идентификатора
                    self.canvas.delete(point["id"])
            self.canvas.delete(self.line_distance_ids_BR)
            self.points_distance.clear()
            self.all_blocks = []
            self.image = self.original_image.copy()
            self.update_image_on_canvas()
        if len(self.main_points_id) == 4:
            line_id = self.canvas.create_line(self.main_points_id[0]["canvas_x"], self.main_points_id[0]["canvas_y"],
                                              self.main_points_id[1]["canvas_x"], self.main_points_id[1]["canvas_y"],
                                              fill='blue', width=2)
            self.line_ids_BR.append(line_id)
            line_id = self.canvas.create_line(self.main_points_id[1]["canvas_x"], self.main_points_id[1]["canvas_y"],
                                              self.main_points_id[2]["canvas_x"], self.main_points_id[2]["canvas_y"],
                                              fill='red', width=2)
            self.line_ids_BR.append(line_id)
            line_id = self.canvas.create_line(self.main_points_id[2]["canvas_x"], self.main_points_id[2]["canvas_y"],
                                              self.main_points_id[3]["canvas_x"], self.main_points_id[3]["canvas_y"],
                                              fill='blue', width=2)
            self.line_ids_BR.append(line_id)
            line_id = self.canvas.create_line(self.main_points_id[0]["canvas_x"], self.main_points_id[0]["canvas_y"],
                                              self.main_points_id[3]["canvas_x"], self.main_points_id[3]["canvas_y"],
                                              fill='red', width=2)
            self.line_ids_BR.append(line_id)

    def _remove_lines(self):
        # Удаляем все линии с тегом "grid_line"
        self.canvas.delete("grid_line")
    def add_lines_frame(self):

        if len(self.grid.allPoints) > 0:


            self.all_blocks=[]
            self.image = self.original_image.copy()
            draw = ImageDraw.Draw(self.image)
            jmin = len(self.grid.allPoints[0])
            jmax = 0
            imin = len(self.grid.allPoints)
            for i in range(len(self.grid.allPoints)):

                dx = []
                dy = []
                # Вычисляем разницы x и y между соседними точками
                for j in range(len(self.grid.allPoints[i]) - 1):
                    dx.append(self.grid.allPoints[i][j + 1][0] - self.grid.allPoints[i][j][0])
                    dy.append(self.grid.allPoints[i][j + 1][1] - self.grid.allPoints[i][j][1])

                # Преобразуем списки dx и dy в массивы NumPy
                dx_array = np.array(dx)
                dy_array = np.array(dy)

                # Подсчитываем положительные и отрицательные разницы по x
                positive_dx_count = np.sum(dx_array > 0)
                negative_dx_count = np.sum(dx_array < 0)
                if positive_dx_count > negative_dx_count:
                    f = True
                    indices_to_delete = []
                    for j in range(len(self.grid.allPoints[i]) - 2, -1, -1):
                        if self.grid.allPoints[i][j+1][0]-self.grid.allPoints[i][j][0]<0:
                            if f is True:
                                indices_to_delete.append(j+1)
                            else:
                                indices_to_delete.append(j)
                        else:
                            f = False
                    new_points = []
                    # Итерируем по элементам allPoints[i]
                    for j in range(len(self.grid.allPoints[i])):
                        # Если индекс не в списке индексов для удаления, добавляем элемент в новый массив
                        if j not in indices_to_delete:
                            new_points.append(self.grid.allPoints[i][j])
                        else:
                            new_points.append(None)

                    self.grid.allPoints[i] = new_points
                if positive_dx_count < negative_dx_count:
                    f = True
                    indices_to_delete = []
                    for j in range(len(self.grid.allPoints[i]) - 2, -1, -1):
                        if self.grid.allPoints[i][j+1][0] - self.grid.allPoints[i][j][0] > 0:
                            if f is True:
                                indices_to_delete.append(j+1)
                            else:
                                indices_to_delete.append(j)
                        else:
                            f = False
                    new_points = []
                    # Итерируем по элементам allPoints[i]
                    for j in range(len(self.grid.allPoints[i])):
                        # Если индекс не в списке индексов для удаления, добавляем элемент в новый массив
                        if j not in indices_to_delete:
                            new_points.append(self.grid.allPoints[i][j])
                        else:
                            new_points.append(None)
                    # Заменяем старый массив новым
                    self.grid.allPoints[i] = new_points


                # Подсчитываем положительные и отрицательные разницы по y
                positive_dy_count = np.sum(dy_array > 0)
                negative_dy_count = np.sum(dy_array < 0)
            for i in range(len(self.grid.allPoints)-1):
                arr = []

                for j in range(len(self.grid.allPoints[0]) - 1):
                    if self.grid.allPoints[i][j] != None and self.grid.allPoints[i][j + 1] != None and self.grid.allPoints[i+1][j] != None and self.grid.allPoints[i+1][j + 1] != None:
                        if (0 <= self.grid.allPoints[i][j][0] <= self.grid.width and
                             0 <= self.grid.allPoints[i][j][1] <= self.grid.height)or (0 <= self.grid.allPoints[i][j + 1][0] <= self.grid.width and
                                 0 <= self.grid.allPoints[i][j + 1][1] <= self.grid.height)or (0 <= self.grid.allPoints[i+1][j][0] <= self.grid.width and
                                 0 <= self.grid.allPoints[i+1][j][1] <= self.grid.height) or (0 <= self.grid.allPoints[i + 1][j + 1][0] <= self.grid.width and
                                 0 <= self.grid.allPoints[i + 1][j + 1][1] <= self.grid.height) :
                            arr.append([(i,j),(i,j+1),(i+1,j),(i+1,j+1)])
                            if jmin >j:
                                jmin = j
                            if jmax < j:
                                jmax = j
                            if imin >i:
                                imin = i
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
                    print(i)
                    self.all_blocks.append(arr)
            self.update_image_on_canvas()
            # Создание Canvas для отображения изображения
            self.canvas2 = Canvas(self.additional_frame, bg="white", width=400, height=400)
            self.canvas2.grid(row=8, column=0, columnspan=3)

            big_img = None
            w = int(self.grid.w) *2
            h = int(self.grid.h) *2
            self.grid.jmin = jmin
            self.grid.jmax = jmax
            self.grid.imin = imin
            big_img_list = []
            for blocks in self.all_blocks:
                img = None
                t= []
                img_list = []  # Список для горизонтального объединения изображений в строке
                ti = 1
                fc = False
                if blocks[0][0][1] > jmin:
                    for i in range(blocks[0][0][1]-jmin):
                        if blocks[0][0][0] == 0 and jmin == 0 and i ==0:
                            if int(self.grid.sizeWH[0] * h) == 0:
                                fc = True
                            t.append(1)
                            img_black = np.zeros((int(h*self.grid.sizeWH[0]), int(w*self.grid.sizeWH[2]), 3), dtype="uint8")
                        elif blocks[0][0][0] == 0:
                            if int(self.grid.sizeWH[0] * h) == 0:
                                fc = True
                            t.append(2)
                            img_black = np.zeros((int(h * self.grid.sizeWH[0]), w, 3), dtype="uint8")
                        elif blocks[0][0][0] == (len(self.grid.allPoints)-2) and jmin == 0 and i ==0:
                            t.append(11)
                            if int(self.grid.sizeWH[1] * h) == 0:
                                fc = True
                            img_black = np.zeros((int(h*self.grid.sizeWH[1]), int(w*self.grid.sizeWH[2]), 3), dtype="uint8")
                        elif blocks[0][0][0] == (len(self.grid.allPoints)-2):
                            t.append(22)
                            if int(self.grid.sizeWH[1] * h) == 0:
                                fc = True
                            img_black = np.zeros((int(h * self.grid.sizeWH[1]), w, 3), dtype="uint8")
                        elif jmin == 0 and i ==0:
                            t.append(3)
                            img_black = np.zeros((h , int(w*self.grid.sizeWH[2]), 3), dtype="uint8")
                        else:
                            t.append(4)
                            img_black = np.zeros((h , w, 3), dtype="uint8")
                        img_list.append(img_black)
                    # if fc == True:
                    #     continue
                t = []
                wp = 0
                hp = 0
                p1= blocks[0][0]
                p2= blocks[0][2]
                p3= 0
                p4= 0
                for p in blocks:
                    p3 = p[1]
                    p4 = p[3]
                    # Левый верхний угол ((0,0))
                    if p[0][0] == 0 and p[0][1] == 0 :
                        t.append(1)
                        wp += int(w*self.grid.sizeWH[2])
                        hp = int(h*self.grid.sizeWH[0])
                    # верхний край
                    elif p[0][0] == 0 and p[0][1] == (len(self.grid.allPoints[0])-2) :
                        t.append(2)
                        wp += int(w*self.grid.sizeWH[3])
                        hp = int(h*self.grid.sizeWH[0])
                    # Левая граница (не угол)
                    elif p[0][0] == 0:
                        t.append(3)
                        wp += w
                        hp = int(h * self.grid.sizeWH[0])
                    # находится в нижнем левом углу
                    elif p[3][0] == (len(self.grid.allPoints)-1) and p[0][1] == 0 :
                        t.append(4)
                        wp += int(w*self.grid.sizeWH[2])
                        hp = int(h*self.grid.sizeWH[1])
                    # Правый нижний угол ((max X, max Y))
                    elif p[0][0] == (len(self.grid.allPoints)-2) and p[0][1] == (len(self.grid.allPoints[0])-2) :
                        t.append(5)
                        wp += int(w*self.grid.sizeWH[3])
                        hp = int(h*self.grid.sizeWH[1])
                    # нижний край
                    elif p[0][0] == (len(self.grid.allPoints)-2):
                        t.append(6)
                        wp += w
                        hp = int(h * self.grid.sizeWH[1])
                        print(66666666666)
                    # левая граница (но не угол)
                    elif p[0][1] == 0 :
                        t.append(8)
                        wp += int(w*self.grid.sizeWH[2])
                        hp = h
                    # правая граница (но не угол)
                    elif p[0][1] == (len(self.grid.allPoints[0])-2) :
                        t.append(9)
                        wp += int(w*self.grid.sizeWH[3])
                        hp = h
                        print(99999999999)
                    # Обычный блок (без границ)
                    else:
                        t.append(7)
                        wp += w
                        hp = h
                    print(t)
                pts1 = np.float32([self.grid.allPoints[p1[0]][p1[1]], self.grid.allPoints[p2[0]][p2[1]], self.grid.allPoints[p3[0]][p3[1]], self.grid.allPoints[p4[0]][p4[1]]])
                pts2 = np.float32(
                    [[0, 0], [0, hp], [int(wp), 0], [int(wp), hp]])
                im = np.array(Image.open(self.path))
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                new_img = cv2.warpPerspective(im, matrix, (int(wp), int(hp)))
                img_list.append(new_img)
                t=[]
                if blocks[len(blocks)-1][0][1] <jmax:
                    for i in range(jmax-blocks[len(blocks)-1][0][1] ):

                        if blocks[0][0][0] == (len(self.grid.allPoints)-2) and jmax == (len(self.grid.allPoints[0])-2) and i == (jmax-blocks[len(blocks)-1][0][1]-1):
                            t.append(1)
                            if int(self.grid.sizeWH[1] * h) == 0:
                                fc = True
                            img_black = np.zeros((int(h*self.grid.sizeWH[1]), int(w*self.grid.sizeWH[3]), 3), dtype="uint8")
                        elif blocks[0][0][0] == (len(self.grid.allPoints)-2):
                            t.append(2)
                            if int(self.grid.sizeWH[1] * h) == 0:
                                fc = True
                            img_black = np.zeros((int(h*self.grid.sizeWH[1]), w, 3), dtype="uint8")
                        elif blocks[0][0][0] == 0 and jmax== (len(self.grid.allPoints[0])-2) and i == (jmax-blocks[len(blocks)-1][0][1]-1):
                            t.append(11)
                            if int(self.grid.sizeWH[0] * h) == 0:
                                fc = True
                            img_black = np.zeros((int(h*self.grid.sizeWH[0]), int(w*self.grid.sizeWH[3]), 3), dtype="uint8")
                        elif blocks[0][0][0] == 0:
                            t.append(21)
                            if int(self.grid.sizeWH[0] * h) == 0:
                                fc = True
                            img_black = np.zeros((int(h*self.grid.sizeWH[0]), w, 3), dtype="uint8")
                        elif jmax == (len(self.grid.allPoints[0])-2) and i ==(jmax-blocks[len(blocks)-1][0][1]-1):
                            t.append(3)
                            img_black = np.zeros((h , int(w* self.grid.sizeWH[3]), 3), dtype="uint8")
                        else:
                            t.append(4)
                            img_black = np.zeros((h , w, 3), dtype="uint8")
                        img_list.append(img_black)
                if fc == True:
                    continue
                img_row = np.concatenate(img_list, axis=1)

                big_img_list.append(img_row)
            # Объединяем все строки изображений по вертикали
            big_img = np.concatenate(big_img_list, axis=0)

            # Загружаем изображение
            original_image = Image.fromarray(big_img)
            self.grid.img_width, self.grid.img_height = original_image.size
            self.zoom_level = 1.0

            self.image_info = ImageEdit(original_image)
            self.image_info.set_canvas(self.canvas2)

#########################    ЛИНИЯ       ##################################################

    def _draw_point_ld(self, event):
        image_x, image_y = self._get_actual_image_coordinates(event)
        # Преобразование координат изображения в координаты на канвасе
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        for point in self.points_distance:
            radius = 5 * self.imscale
            if (point["image_x"] - radius <= image_x <= point["image_x"] + radius and
                    point["image_y"] - radius <= image_y <= point["image_y"] + radius):
                return

        if len(self.grid.points_distance) < 2:
            x,y = self._get_actual_image_coordinates(event)
            if self.grid.check_point_in_blocks((x,y), self.all_blocks):
                self.grid.points_distance.append((x, y))
                radius = 5 * self.imscale  # Радиус точки
                point_id = self.canvas.create_oval(
                    canvas_x - radius, canvas_y - radius,
                    canvas_x + radius, canvas_y + radius,
                    outline='red', width=4
                )
                self.points_distance.append({
                    "id": point_id,
                    "image_x": image_x,
                    "image_y": image_y,
                    "canvas_x": canvas_x,
                    "canvas_y": canvas_y
                })
            if len(self.points_distance) == 2:
                self.line_distance_ids_BR = self.canvas.create_line(self.points_distance[0]["canvas_x"],
                                                                    self.points_distance[0]["canvas_y"],
                                                                    self.points_distance[1]["canvas_x"],
                                                                    self.points_distance[1]["canvas_y"],
                                                                    fill='red', width=2)
                self.grid.get_dist(self.all_blocks, self.image_info,self.additional_frame)
                self._update_canvasXY()

    def _move_point_ld(self, event):
        image_x, image_y = self._get_actual_image_coordinates(event)
        # Получение текущих координат курсора
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        # Проверка, если курсор находится в пределах какой-либо точки
        for i,point in enumerate(self.points_distance):
            radius = 5 * self.imscale
            if (point["image_x"] - radius <= image_x <= point["image_x"] + radius and
                    point["image_y"] - radius <= image_y <= point["image_y"] + radius) and self.grid.check_point_in_blocks((image_x, image_y), self.all_blocks):
                # Обновление координат точки
                self.canvas.coords(
                    point["id"],
                    canvas_x - radius, canvas_y - radius,
                    canvas_x + radius, canvas_y + radius
                )
                # Пересчет координат на изображении
                bbox = self.canvas.bbox(self.image_container)
                # image_x = int((canvas_x - bbox[0]) / self.imscale)
                # image_y = int((canvas_y - bbox[1]) / self.imscale)
                # Обновляем координаты точки
                point["canvas_x"] = canvas_x
                point["canvas_y"] = canvas_y
                self.grid.points_distance[i] = (image_x, image_y)
                point["image_x"] = image_x
                point["image_y"] = image_y

        self._update_canvasXY()
        if len(self.points_distance) == 2:
            self.canvas.delete(self.line_distance_ids_BR)
            self.line_distance_ids_BR = self.canvas.create_line(self.points_distance[0]["canvas_x"],
                                                                self.points_distance[0]["canvas_y"],
                                                                self.points_distance[1]["canvas_x"],
                                                                self.points_distance[1]["canvas_y"],
                                                                fill='red', width=2)
            self.grid.get_dist(self.all_blocks, self.image_info,self.additional_frame)


    def start_line_selection(self, root):
        self._bind_line()
        self.root = root

    def find_tracks(self):
        self.ai.getTraces(self.path)
        draw = ImageDraw.Draw(self.image)
        lines = []


        for obj in self.ai.objects_points:
            for i in range(len(obj)-1):
                event = Event(obj[i][0], obj[i][1])
                x, y = self._get_actual_image_coordinates(event)
                event = Event(obj[i+1][0], obj[i+1][1])
                x2, y2 = self._get_actual_image_coordinates(event)
                if self.grid.check_point_in_blocks((x, y), self.all_blocks) and self.grid.check_point_in_blocks((x2, y2), self.all_blocks):
                    p1 = self.grid.get_point_2D(self.all_blocks, obj[i])
                    p2 = self.grid.get_point_2D(self.all_blocks, obj[i + 1])
                    lines.append([p1,p2])

                draw.line([tuple(obj[i]), tuple(obj[i+1])], fill="cyan", width=6)
            draw.line([tuple(obj[0]), tuple(obj[len(obj)-1])], fill="cyan", width=6)
            event = Event(obj[0][0], obj[0][1])
            x, y = self._get_actual_image_coordinates(event)
            event = Event(obj[len(obj)-1][0], obj[len(obj)-1][1])
            x2, y2 = self._get_actual_image_coordinates(event)
            if self.grid.check_point_in_blocks((x, y), self.all_blocks) and self.grid.check_point_in_blocks((x2, y2),
                                                                                                            self.all_blocks):
                p1 = self.grid.get_point_2D(self.all_blocks, obj[0])
                p2 = self.grid.get_point_2D(self.all_blocks, obj[len(obj)-1])
                lines.append([p1, p2])
        if self.image_info:
            self.image_info.create_line_traces(lines)
        self.update_image_on_canvas()


    def Close_grid(self, root):
        self._unbind_grid()
        self._unbind_line()
        if self.line_ids_BR:
            self._remove_lines_BR()
        self.remove_additional_frame()
        if self.additional_frame:
            self.additional_frame.destroy()
        self.image = self.original_image.copy()
        self.update_image_on_canvas()
        self.canvas.delete(self.line_distance_ids_BR)
        self.canvas.delete(self.main_points_id)
        self.canvas.delete(self.points_distance)
        for point in self.main_points_id:
            self.canvas.delete(point["id"])
        for point in self.points_distance:
            self.canvas.delete(point["id"])
        self.main_points_id = []
        self.points_distance = []
        self.points_distance.clear()
        self.grid = Grid()  # Initialize or adjust as needed
        self.main_points_id = []
        self.points_distance = []
        self.line_distance_ids_BR= []
        self.right_frame = None  # Or replace with actual initialization
        self.additional_frame = None  # Атрибут для хранения дополнительного фрейма

        self.line_ids_BR= []


        self.root = root

    def _bind_line(self):
        self._unbind_grid()
        self.canvas.bind("<ButtonPress-1>", self._draw_point_ld)
        self.canvas.bind("<B1-Motion>", self._move_point_ld)

    def _unbind_line(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")

        self.canvas["cursor"] = ""