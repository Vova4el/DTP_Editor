from tkinter import *
from tkinter import filedialog as fd
from tkinter.ttk import Notebook
from tkinter import messagebox as mb
from PIL import Image, ImageFilter, ImageEnhance
import os
import pyperclip
import json

from Frame.frame import frame
from image_grid import ImageGrid
from image_info import ImageInfo
from enhance_slider_window import EnhanceSliderWindow
from Dialog.input_dialog import InputDialog

CONFIG_FILE = 'config.json'


class PyPhotoEditor:
    def __init__(self):
        self.root = Tk()
        self.image_tabs = Notebook(self.root)
        self.opened_images = []
        self.last_viewed_images = []

        self.init()

        self.open_recent_menu = None

    def init(self):
        self.root.title("DTP_Editor")
        # self.root.iconbitmap("resources/giga_dps.ico")
        self.image_tabs.enable_traversal()

        self.root.bind("<Escape>", self._close)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"opened_images": [], "last_viewed_images": []}, f)
        else:
            self.load_images_from_config()

    def run(self):
        self.draw_menu()
        self.draw_widgets()

        self.root.mainloop()

    def draw_menu(self):
        menubar = Menu(self.root)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_new_images)


        self.open_recent_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Открыть недавнее", menu=self.open_recent_menu)
        for path in self.last_viewed_images:
            self.open_recent_menu.add_command(label=path, command=lambda x=path: self.add_new_image(x))

        file_menu.add_separator()
        file_menu.add_command(label="Сохранить", command=self.save_current_image)
        file_menu.add_command(label="Сохранить как", command=self.save_image_as)
        file_menu.add_command(label="Сохранить всё", command=self.save_all_changes)
        file_menu.add_separator()
        file_menu.add_cascade(label="Закрыть изображение", command=self.close_current_image)
        file_menu.add_separator()
        file_menu.add_cascade(label="Удалить изображение", command=self.delete_current_image)
        file_menu.add_cascade(label="Переместить изображение", command=self.move_current_image)
        file_menu.add_separator()
        clipboard_menu = Menu(file_menu, tearoff=0)
        clipboard_menu.add_command(label="Добавить название изображения в буфер обмена", command=lambda: self.save_to_clipboar("name"))
        clipboard_menu.add_command(label="Добавить каталог изображений в буфер обмена",
                                   command=lambda: self.save_to_clipboar("dir"))
        clipboard_menu.add_command(label="Добавить путь к изображению в буфер обмена", command=lambda: self.save_to_clipboar("path"))
        file_menu.add_cascade(label="Буфер обмена", menu=clipboard_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._close)
        menubar.add_cascade(label="Файл", menu=file_menu)

        edit_menu = Menu(menubar, tearoff=0)

        rotate_menu = Menu(edit_menu, tearoff=0)

        rotate_menu.add_cascade(label="Повернуть вправо на 90", command=lambda: self.rotate_current_image(-90))
        rotate_menu.add_cascade(label="Повернуть влево на 90", command=lambda: self.rotate_current_image(90))
        rotate_menu.add_cascade(label="Повернуть на 180", command=lambda: self.rotate_current_image(180))

        flip_menu = Menu(edit_menu, tearoff=0)
        flip_menu.add_command(label="Отзеркалить по горизонтали",
                              command=lambda: self.flip_current_image(Image.FLIP_LEFT_RIGHT))
        flip_menu.add_command(label="Отзеркалить по вертикали", command=lambda: self.flip_current_image(Image.FLIP_TOP_BOTTOM))

        resize_menu = Menu(edit_menu, tearoff=0)
        resize_menu.add_command(label="25% от оригинального размера", command=lambda: self.resize_current_image(25))
        resize_menu.add_command(label="50% от оригинального размера", command=lambda: self.resize_current_image(50))
        resize_menu.add_command(label="75% от оригинального размера", command=lambda: self.resize_current_image(75))
        resize_menu.add_command(label="125% от оригинального размера", command=lambda: self.resize_current_image(125))
        resize_menu.add_command(label="150% от оригинального размера", command=lambda: self.resize_current_image(150))
        resize_menu.add_command(label="200% от оригинального размера", command=lambda: self.resize_current_image(200))

        filter_menu = Menu(edit_menu, tearoff=0)
        filter_menu.add_command(label="Размытие", command=lambda: self.apply_filter_to_current_image(ImageFilter.BLUR))
        filter_menu.add_command(label="Контрастность",
                                command=lambda: self.apply_filter_to_current_image(ImageFilter.SHARPEN))
        filter_menu.add_command(label="Контуры",
                                command=lambda: self.apply_filter_to_current_image(ImageFilter.CONTOUR))
        filter_menu.add_command(label="Увеличить детализированность рисунка",
                                command=lambda: self.apply_filter_to_current_image(ImageFilter.DETAIL))
        filter_menu.add_command(label="Сглаживание",
                                command=lambda: self.apply_filter_to_current_image(ImageFilter.SMOOTH))

        crop_menu = Menu(edit_menu, tearoff=0)
        crop_menu.add_command(label="Начать выделение", command=self.start_crop_selection_of_current_image)
        crop_menu.add_command(label="Обрезать выделенное", command=self.crop_selection_of_current_image)
        crop_menu.add_command(label="Закрыть", command=self.cancel_selection_of_current_image)

        grid_menu = Menu(edit_menu, tearoff=0)
        grid_menu.add_command(label="Начать выделение", command=self.start_grid_selection_of_current_image)
        grid_menu.add_command(label="Наложить сетку", command=self.make_grid)
        grid_menu.add_command(label="Начать выделять линию для вычисления дистанции", command=self.start_line_selection)
        grid_menu.add_command(label="Найти следы", command=self.find_tracks)
        grid_menu.add_command(label="Закрыть", command=self.Close_grid)

        convert_menu = Menu(edit_menu, tearoff=0)
        convert_menu.add_command(label="Черно белый", command=lambda: self.convert_current_inside_image("1"))
        convert_menu.add_command(label="Оттенки серого", command=lambda: self.convert_current_inside_image("L"))
        convert_menu.add_command(label="RGB", command=lambda: self.convert_current_inside_image("RGB"))
        convert_menu.add_command(label="RGBA", command=lambda: self.convert_current_inside_image("RGBA"))
        convert_menu.add_command(label="CMYK", command=lambda: self.convert_current_inside_image("CMYK"))
        convert_menu.add_command(label="LAB", command=lambda: self.convert_current_inside_image("LAB"))
        convert_menu.add_command(label="HSV", command=lambda: self.convert_current_inside_image("HSV"))
        convert_menu.add_command(label="Roll RGB colors", command=lambda: self.convert_current_inside_image("roll"))
        convert_menu.add_command(label="Красный", command=lambda: self.convert_current_inside_image("R"))
        convert_menu.add_command(label="Зелёный", command=lambda: self.convert_current_inside_image("G"))
        convert_menu.add_command(label="Синий", command=lambda: self.convert_current_inside_image("B"))

        enhance_menu = Menu(edit_menu, tearoff=0)
        enhance_menu.add_command(label="Цвет", command=lambda: self.enhance_current_image("Цвет", ImageEnhance.Color))
        enhance_menu.add_command(label="Контраст", command=lambda: self.enhance_current_image("Контраст", ImageEnhance.Contrast))
        enhance_menu.add_command(label="Яркость", command=lambda: self.enhance_current_image("Яркость", ImageEnhance.Brightness))
        enhance_menu.add_command(label="Четкость", command=lambda: self.enhance_current_image("Четкость", ImageEnhance.Sharpness))

        edit_menu.add_cascade(label="Повернуть", menu=rotate_menu)
        edit_menu.add_cascade(label="Отзеркалить", menu=flip_menu)
        edit_menu.add_cascade(label="Изменить размер", menu=resize_menu)
        edit_menu.add_separator()
        edit_menu.add_cascade(label="Фильтер", menu=filter_menu)
        edit_menu.add_cascade(label="Конвертировать", menu=convert_menu)
        edit_menu.add_cascade(label="Эффекты", menu=enhance_menu)
        edit_menu.add_separator()
        edit_menu.add_cascade(label="Обрезать", menu=crop_menu)
        edit_menu.add_separator()
        edit_menu.add_cascade(label="Построить сетку", menu=grid_menu)

        menubar.add_cascade(label="Редактировать", menu=edit_menu)

        self.root.config(menu=menubar)

    def update_open_recent_menu(self):
        if self.open_recent_menu is None:
            return
        
        self.open_recent_menu.delete(0,"end")
        for path in self.last_viewed_images:
            self.open_recent_menu.add_command(label=path, command=lambda x=path: self.add_new_image(x))

    def draw_widgets(self):
        self.image_tabs.pack(side=LEFT, fill=BOTH, expand=1)  # Основные виджеты



    def dummy_command(self):
        # Пример метода, который вызывается при нажатии на кнопку
        mb.showinfo("Информация", "Эта кнопка еще не настроена!")

    def load_images_from_config(self):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        self.last_viewed_images = config["last_viewed_images"]
        paths = config["opened_images"]
        for path in paths:
            self.add_new_image(path)

    def open_new_images(self):
        image_paths = fd.askopenfilenames(filetypes=(("Image Files", "*.jpg;*.jpeg;*.png"),))
        for image_path in image_paths:
            self.add_new_image(image_path)
            if image_path not in self.last_viewed_images:
                self.last_viewed_images.append(image_path)
            else:
                self.last_viewed_images.remove(image_path)
                self.last_viewed_images.append(image_path)
            if len(self.last_viewed_images) > 5:
                del self.last_viewed_images[0]

        self.update_open_recent_menu()
    def add_new_image(self, image_path):
        if not os.path.isfile(image_path):
            if image_path in self.last_viewed_images:
                self.last_viewed_images.remove(image_path)
                self.update_open_recent_menu()
            return
        opened_images = [info.path for info in self.opened_images]
        if image_path in opened_images:
            index = opened_images.index(image_path)
            self.opened_images.index(image_path)
            self.image_tabs.select(index)
            return

        image = Image.open(image_path)
        image_tab = Frame(self.image_tabs)
        image_info = ImageGrid(image, image_path, image_tab)
        self.opened_images.append(image_info)

        #make the canvas expandable
        image_tab.rowconfigure(0, weight=1)
        image_tab.columnconfigure(0, weight=1)

        canvas = Canvas(image_tab, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        canvas.update() # wait till canvas is created

        image_info.set_canvas(canvas)
        # Добавление дополнительного фрейма
        self.add_additional_frame(image_tab)

        self.image_tabs.add(image_tab, text=image_info.filename())
        self.image_tabs.select(image_tab)

    def add_additional_frame(self, parent_frame):
        # Создание дополнительного фрейма
        additional_frame = Frame(parent_frame, bg="lightgrey")
        additional_frame.grid(row=1, column=0, sticky="nsew")

        # # Добавление виджетов в дополнительный фрейм
        # Label(additional_frame, text="Это дополнительный фрейм внутри вкладки", bg="lightgrey").pack(pady=10)

        return additional_frame

    def current_image(self):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return None
        tab_number = self.image_tabs.index(current_tab)
        return self.opened_images[tab_number]

    def save_current_image(self):
        image = self.current_image()
        if not image:
            return
        if not image.unsaved:
            return
        image.save()
        self.image_tabs.add(image.tab, text=image.filename())

    def save_image_as(self):
        image = self.current_image()
        if not image:
            return
        try:
            image.save_as()
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Сбой сохранения", str(e))

    def save_all_changes(self):
        for image_info in self.opened_images:
            if not image_info.unsaved:
                continue
            image_info.save()
            self.image_tabs.tab(image_info.tab, text=image_info.filename())

    def close_current_image(self):
        image = self.current_image()
        if not image:
            return
        if image.unsaved:
            if not mb.askyesno("Несохранённые изменения", "имеются несохранённые изменения! Выйти в любом случае?"):
                return

        image.close()
        self.image_tabs.forget(image.tab)
        self.opened_images.remove(image)

    def delete_current_image(self):
        image = self.current_image()
        if not image:
            return
        if not mb.askokcancel("Удалить изображение",
                              "Вы уверены, что хотите удалить изображение?\nЭту операцию не отменить"):
            return

        image.delete()
        self.image_tabs.forget(image.tab)
        self.opened_images.remove(image)

    def move_current_image(self):
        image = self.current_image()
        if not image:
            return

        image.move()
        self.update_image_inside_app(image)

    def update_image_inside_app(self, image_info):
        image_info.update_image_on_canvas()
        self.image_tabs.tab(image_info.tab, text=image_info.filename())

    def rotate_current_image(self, degrees=1):
        image = self.current_image()
        if not image:
            return

        try:
            image.rotate(degrees)
            image.unsaved = True
            image = image.rotate(degrees, expand=True)
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Ошибка поворота", str(e))

    def flip_current_image(self, mode):
        image = self.current_image()
        if not image:
            return

        try:
            image.flip(mode)
            image.unsaved = True
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Ошибка отзеркаливания", str(e))

    def resize_current_image(self, percents):
        image = self.current_image()
        if not image:
            return

        try:
            image.resize(percents)
            image.unsaved = True
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Ошибка изменения размера", str(e))

    def apply_filter_to_current_image(self, filter_type):
        image = self.current_image()
        if not image:
            return

        image.filter(filter_type)
        image.unsaved = True
        self.update_image_inside_app(image)

    def start_crop_selection_of_current_image(self):
        image = self.current_image()
        if not image:
            return

        image.start_crop_selection()

    def crop_selection_of_current_image(self):
        image = self.current_image()
        if not image:
            return

        try:
            image.crop_selected_area()
            image.unsaved = True
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Crop selection error", str(e))

    def cancel_selection_of_current_image(self):
        image = self.current_image()
        if not image:
            return

        try:
            image.cancel_crop_selection()
        except ValueError as e:
            mb.showerror("Crop selection error", str(e))

    def convert_current_inside_image(self, mode):
        image = self.current_image()
        if not image:
            return
        try:
            image.convert(mode)
            image.unsaved = True
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Convert error", str(e))

    def start_grid_selection_of_current_image(self):
        image = self.current_image()
        if not image:
            return

        image.start_grid_selection(self.root)

    def make_grid(self):
        image = self.current_image()
        if not image:
            return
        image.make_grid()

    def start_line_selection(self):
        image = self.current_image()
        if not image:
            return
        image.start_line_selection(self.root)

    def find_tracks(self):
        image = self.current_image()
        if not image:
            return
        image.find_tracks()


    def Close_grid(self):
        image = self.current_image()
        if not image:
            return
        image.Close_grid(self.root)

    def enhance_current_image(self, name, enhance):
        image = self.current_image()
        if not image:
            return
        EnhanceSliderWindow(self.root, name, enhance, image, self.update_image_inside_app)

    def save_to_clipboar(self, mode):
        image = self.current_image()
        if not image:
            return

        if mode == "name":
            pyperclip.copy(image.filename(no_star=True))
        if mode == "dir":
            pyperclip.copy(image.directory(no_star=True))
        if mode == "path":
            pyperclip.copy(image.full_path(no_star=True))

    def save_images_to_config(self):
        paths = [info.full_path(no_star=True) for info in self.opened_images]
        images = {"opened_images": paths, "last_viewed_images": self.last_viewed_images}
        with open(CONFIG_FILE, "w") as f:
            json.dump(images, f, indent=4)

    def unsaved_images(self):
        for info in self.opened_images:
            if info.unsaved:
                return True
        return False

    def _close(self, event=None):
        if self.unsaved_images():
            if not mb.askyesno("Несохранённые изменения", "имеются несохранённые изменения! Выйти в любом случае?"):
                return
        self.save_images_to_config()
        self.root.quit()


if __name__ == "__main__":
    PyPhotoEditor().run()
