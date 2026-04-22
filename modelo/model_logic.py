import os
import numpy as np
from PIL import Image, ImageOps
from tf_keras.models import load_model

class Model:
    """
    Clase encargada de la lógica de Inteligencia Artificial (Backend).
    Maneja la carga del modelo y las predicciones matemáticas.
    """
    def __init__(self, model_path="keras_model.h5", labels_path="labels.txt"):
        self.model_path = model_path
        self.labels_path = labels_path
        self.model = None
        self.class_names = []
        self.is_loaded = False

    def load(self):
        """Carga el modelo y las etiquetas en la memoria."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"No se encontró '{self.model_path}'.")
        if not os.path.exists(self.labels_path):
            raise FileNotFoundError(f"No se encontró '{self.labels_path}'.")

        self.model = load_model(self.model_path, compile=False)
        
        with open(self.labels_path, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]
        
        np.set_printoptions(suppress=True)
        self.is_loaded = True

    def predict(self, image_path):
        """Procesa una imagen y devuelve el diagnóstico y las probabilidades."""
        if not self.is_loaded:
            raise RuntimeError("El modelo no está cargado. Llama a load() primero.")
        
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        image = Image.open(image_path).convert("RGB")
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        data[0] = normalized_image_array
        
        prediction = self.model.predict(data, verbose=0)
        index = np.argmax(prediction)
        class_name = self.class_names[index].strip()
        
        if len(class_name) > 2 and class_name[1] == ' ':
            class_name = class_name[2:]
            
        confidence_score = float(prediction[0][index])
        
        predictions_list = []
        for i, class_n in enumerate(self.class_names):
            class_display = class_n.strip()
            if len(class_display) > 2 and class_display[1] == ' ':
                class_display = class_display[2:]
            predictions_list.append((class_display, float(prediction[0][i])))
        
        predictions_list.sort(key=lambda x: x[1], reverse=True)
        
        return class_name, confidence_score, predictions_list