import os
import cv2
import numpy as np
from ultralytics import YOLO
import torch

class AI:
    def __init__(self):
        self.objects_points = []  # Список для хранения точек контуров объектов
        self.objects_confidences = []  # Список для хранения точности (confidence) каждого объекта

    def add_object(self, points, confidence):
        """Добавляет точки контура объекта и его точность в списки."""
        self.objects_points.append(points)
        self.objects_confidences.append(confidence)

    def getTraces(self,path):
        # Разрешение проблемы с библиотекой KMP (если возникает)
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

        # Загрузка обученной модели YOLOv8
        model = YOLO('ai/best.pt')  # Путь к сохранённой модели

        # Путь к изображению для инференса
        image_path = path  # путь к изображению

        # Выполнение инференса
        results = model.predict(source=image_path, conf=0.25)  # conf=0.75 - минимальная уверенность для детекции

        # очищаем
        self.objects_points = []
        self.objects_confidences = []

        # Обработка результатов
        for result in results:
            # Проверяем, есть ли маски сегментации в результате
            if result.masks is not None:

                masks = result.masks.xy
                # Извлекаем точность (confidence) для каждого объекта
                confidences = result.boxes.conf.cpu().numpy()  # Перемещаем на CPU, если нужно

                # Обрабатываем каждый объект
                for i, mask in enumerate(masks):  # Итерируем по каждому объекту
                    points = []  # Создаем отдельный список точек для каждого объекта
                    for x, y in mask:  # Итерируем по точкам внутри объекта
                        points.append([round(x), round(y)])  # Округляем координаты

                    # Добавляем объект с его точками и уверенностью
                    self.add_object(points, confidences[i])

