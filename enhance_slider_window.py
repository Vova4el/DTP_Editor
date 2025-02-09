from tkinter import *


class EnhanceSliderWindow(Toplevel):
    def __init__(self, root, name, enhance, image_info, update_method):
        super().__init__(root)

        self.name = name
        self.image_info = image_info
        self.original = image_info.image
        self.enhance = image_info.get_enhancer(enhance)
        self.update_method = update_method

        self.init()

        self.factor = DoubleVar(value=1.0)

        self.scroll = Scale(self, label=self.name, from_=0.0, to=3.0, resolution=0.1, variable=self.factor,
                            orient=HORIZONTAL, command=self.value_changed)
        self.apply = Button(self,text="Применить", command=self.apply)
        self.cancel = Button(self,text="Отменить", command=self.cancel)

        self.draw_widgets()


    def init(self):
        self.title(f"Эффект {self.name}")
        self.grab_focus()

    def grab_focus(self):
        self.grab_set()
        self.focus_set()

    def draw_widgets(self):
        self.scroll.pack(fill="x",expand=1, pady=5, padx=5)
        self.apply.pack(side="left",expand=1, pady=5, padx=5)
        self.cancel.pack(side="left",expand=1, pady=5, padx=5)

    def value_changed(self, value):
        self.image = self.enhance.enhance(self.factor.get())
        self.image_info.set_image(self.image)
        self.image_info.update_image_on_canvas()

    def apply(self):
        self.image_info.unsaved = True
        self.update_method(self.image_info)
        self.close()

    def cancel(self):
        self.image_info.set_image(self.original)
        self.image_info.update_image_on_canvas()

        self.update_method(self.image_info)
        self.close()

    def close(self):
        self.destroy()





