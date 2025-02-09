
from tkinter import Label, Entry, Button, Toplevel, messagebox
from PIL import ImageTk

class InputDialog(Toplevel):
    def __init__(self, parent, image_array, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title("Input Dialog")
        # Загружаем и отображаем изображение
        image = image_array
        image.thumbnail((300, 300))  # Устанавливаем максимальный размер изображения
        self.photo = ImageTk.PhotoImage(image)

        self.image_label = Label(self, image=self.photo)
        self.image_label.grid(row=0, column=0, columnspan=3)

        # Поле ввода 1
        self.label1 = Label(self, text="Введите длинну красных сторон:")
        self.label1.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.entry1 = Entry(self)
        self.entry1.grid(row=1, column=1, padx=(0, 0), pady=10, sticky="e")

        self.label3 = Label(self, text="см")
        self.label3.grid(row=1, column=2, padx=(0, 5), pady=10, sticky="w")

        # Поле ввода 2
        self.label2 = Label(self, text="Введите длинну синих сторон:")
        self.label2.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.entry2 = Entry(self)
        self.entry2.grid(row=2, column=1, padx=(0, 0), pady=10, sticky="e")
        self.label4 = Label(self, text="см")
        self.label4.grid(row=2, column=2, padx=(0, 5), pady=10, sticky="w")
        # Кнопка подтверждения
        self.ok_button = Button(self, text="OK", command=self.on_ok)
        self.ok_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.result = None

    def on_ok(self):
        input1 = self.entry1.get()
        input2 = self.entry2.get()

        # Проверка, что оба ввода - вещественные числа
        try:
            float(input1)
            float(input2)
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите вещественные числа в оба поля.")
        else:
            self.result = (input1, input2)
            self.destroy()
