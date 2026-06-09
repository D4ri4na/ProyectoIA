import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report

print("Versión de TensorFlow:", tf.__version__)

# 1. Configuración de rutas (Ruta absoluta para evitar errores)
dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset')
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

if not os.path.exists(dataset_dir):
    raise FileNotFoundError(f"¡Error! No se encontró la carpeta: {dataset_dir}")

print("\nCargando imágenes...")
train_dataset = image_dataset_from_directory(
    dataset_dir, validation_split=0.2, subset="training", 
    seed=123, image_size=IMG_SIZE, batch_size=BATCH_SIZE
)

val_dataset = image_dataset_from_directory(
    dataset_dir, validation_split=0.2, subset="validation", 
    seed=123, image_size=IMG_SIZE, batch_size=BATCH_SIZE
)

class_names = train_dataset.class_names
print(f"Clases detectadas: {class_names}")

# 3. Data Augmentation
data_augmentation = tf.keras.Sequential([
  layers.RandomFlip('horizontal'),
  layers.RandomRotation(0.2),
  layers.RandomZoom(0.2),
])

# 4. Cargar Arquitectura MobileNetV2
preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input
base_model = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights='imagenet')
base_model.trainable = False 

# 5. Construir el modelo final
inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
x = data_augmentation(inputs)
x = preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(len(class_names), activation='softmax')(x)
model = tf.keras.Model(inputs, outputs)

# 6. Compilar
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 7. Entrenar
print("\nIniciando el entrenamiento...")
history = model.fit(train_dataset, validation_data=val_dataset, epochs=15)

# =========================================================================
# 8. GENERACIÓN DE GRÁFICAS PARA LA DOCUMENTACIÓN
# =========================================================================
print("\n--- GENERANDO GRÁFICAS ---")

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.title('Precisión por Época')
plt.xlabel('Épocas')
plt.ylabel('Precisión')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Entrenamiento')
plt.plot(history.history['val_loss'], label='Validación')
plt.title('Pérdida por Época')
plt.xlabel('Épocas')
plt.ylabel('Pérdida')
plt.legend()
plt.grid(True)

ruta_curvas = os.path.join(os.path.dirname(__file__), 'curvas_entrenamiento.png')
plt.savefig(ruta_curvas, dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Curvas guardadas en: {ruta_curvas}")

print("Evaluando validación para la Matriz de Confusiones...")
y_true = []
y_pred = []

for images, labels in val_dataset:
    y_true.extend(labels.numpy())
    preds = model.predict(images, verbose=0)
    y_pred.extend(np.argmax(preds, axis=1))

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.title('Matriz de Confusión')
plt.ylabel('Clase Real')
plt.xlabel('Predicción de la IA')

ruta_matriz = os.path.join(os.path.dirname(__file__), 'matriz_confusion.png')
plt.savefig(ruta_matriz, dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Matriz guardada en: {ruta_matriz}")

ruta_reporte = os.path.join(os.path.dirname(__file__), 'reporte_metricas.txt')
with open(ruta_reporte, 'w') as f:
    f.write(classification_report(y_true, y_pred, target_names=class_names))

# =========================================================================
# 9. EXPORTAR A TFLITE (MÉTODO ROBUSTO)
# =========================================================================
print("\n--- EXPORTANDO A FORMATO MÓVIL ---")
temp_model_dir = os.path.join(os.path.dirname(__file__), 'temp_saved_model')

# Guardamos el modelo en una carpeta temporal primero (evita el bug de memoria)
tf.saved_model.save(model, temp_model_dir)

# Convertimos desde la carpeta temporal
converter = tf.lite.TFLiteConverter.from_saved_model(temp_model_dir)
tflite_model = converter.convert()

tflite_path = os.path.join(os.path.dirname(__file__), 'modelo_cana_offline.tflite')
with open(tflite_path, 'wb') as f:
  f.write(tflite_model)

print(f"\n✅ ¡Éxito Total! Revisa tu carpeta para ver las imágenes y el modelo.")