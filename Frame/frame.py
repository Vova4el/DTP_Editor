from tkinter import *
from tkinter import messagebox


class frame:
    def __init__(self):
        self.right_frame = None  # Изначально правый фрейм не создается

    def create_entry(self, row, column, value):
        entry = Entry(self.right_frame)
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

    def add_additional_frame(self, parent_frame,grid):
        if self.right_frame:
            self.right_frame.destroy()

            # Создаем новый дополнительный фрейм
        self.right_frame = Frame(parent_frame, bg="lightgrey")
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_columnconfigure(1, weight=0)

        self.label1 = Label(self.right_frame, text="Введите длину красных сторон:")
        self.label1.grid(row=1, column=0, padx=0, pady=5, sticky='w')

        self.entry1 = Entry(self.right_frame)
        self.entry1.grid(row=1, column=1, padx=0, pady=0, sticky='w')
        self.entry1.insert(0, grid.w)

        self.label2 = Label(self.right_frame, text="Введите длину синих сторон:")
        self.label2.grid(row=2, column=0, padx=0, pady=0, sticky='w')

        self.entry2 = Entry(self.right_frame)
        self.entry2.grid(row=2, column=1, padx=0, pady=0, sticky='w')
        self.entry2.insert(0, grid.h)

        # Создаем кнопку, которая будет выводить содержимое поля ввода
        self.show_button = Button(self.right_frame, text="Показать содержимое",
                                  command=self.show_entry_content)
        self.show_button.grid(row=3, column=0, padx=0, pady=0, sticky='w')

        self.labelX = Label(self.right_frame, text="X")
        self.labelX.grid(row=3, column=1, padx=0, pady=0, sticky='w')

        self.labelY = Label(self.right_frame, text="Y")
        self.labelY.grid(row=3, column=2, padx=0, pady=0, sticky='w')

        self.entryX1 = self.create_entry(4, 1, grid.points[0][0])
        self.entryY1 = self.create_entry(4, 2, grid.points[0][1])

        self.entryX2 = self.create_entry(5, 1, grid.points[1][0])
        self.entryY2 = self.create_entry(5, 2, grid.points[1][1])

        self.entryX3 = self.create_entry(6, 1, grid.points[2][0])
        self.entryY3 = self.create_entry(6, 2, grid.points[2][1])

        self.entryX4 = self.create_entry(7, 1, grid.points[3][0])
        self.entryY4 = self.create_entry(7, 2, grid.points[3][1])