import tkinter as tk

def on_slider_change(value):
    # Эта функция вызывается при движении ползунка
    label.config(text=f"Текущее значение: {value}")

root = tk.Tk()
root.title("Интерактивный слайдер")

# Создаем горизонтальный слайдер (от 0 до 100)
slider = tk.Scale(
    root,
    from_=10,          # минимальное значение
    to=100,           # максимальное значение
    orient=tk.HORIZONTAL,  # ориентация (можно VERTICAL)
    command=on_slider_change  # функция, вызываемая при изменении
)
slider.pack(pady=20, padx=20)

# Метка для отображения значения
label = tk.Label(root, text="Текущее значение: 10")
label.pack()

root.mainloop()