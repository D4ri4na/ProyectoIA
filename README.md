# 🌾 Sistema Inteligente de Diagnóstico Foliar para Caña de Azúcar

## 📌 Descripción del Proyecto

Esta plataforma es una solución tecnológica integral diseñada para automatizar y democratizar el diagnóstico fitopatológico en el sector agroindustrial de Santa Cruz, Bolivia. El proyecto utiliza Inteligencia Artificial (Redes Neuronales Convolucionales) entrenada con un banco fotográfico híbrido de **2,521 imágenes reales** del tejido foliar de la caña de azúcar (*Saccharum officinarum*).

El repositorio documenta la evolución arquitectónica del sistema en dos grandes fases:

1. **Fase 1 (Plataforma Web):** Arquitectura tradicional Cliente-Servidor impulsada por Flask.
2. **Fase 2 (Aplicación Móvil - *Edge Computing*):** Aplicación nativa autónoma que procesa las imágenes y devuelve diagnósticos matemáticos sin necesidad de conexión a internet, ideal para zonas rurales.

## 🔗 Recursos de la Defensa

* **📄 Documentación del Proyecto:** [https://docs.google.com/document/d/1vAMUaaMsnxUT14SCvp_RCP0-2i-kv4qgUWhQa0mgq-o/edit?tab=t.y3h4t2ri67h8]
* **📊 Presentación y Diapositivas:** [https://canva.link/fajrxmtpr6tt7wc]

## 🎯 Enfermedades Detectables y Capacidades

El modelo es capaz de clasificar hojas sanas y diagnosticar cuatro de las enfermedades de mayor impacto económico en la región, calculando su distribución de confianza (porcentajes de probabilidad) en milisegundos:

1. **Hoja Sana (Control)**
2. **Roya** (*Puccinia melanocephala*)
3. **Muermo Rojo** (*Colletotrichum falcatum*)
4. **Virus del Mosaico** (SCMV)
5. **Síndrome de la Hoja Amarilla** (SCYLV)

*Precisión predictiva global validada: **>80% con Fine-Tuning y Parada Temprana***

---

## 📁 Estructura General del Repositorio

El repositorio se divide en tres módulos independientes:

```text
/
├── web/                         # MÓDULO 1: Aplicación Web Original (Flask)
│   ├── app.py                   # Servidor backend
│   ├── keras_model.h5           # Modelo IA en formato Keras
│   ├── index.html / app.js      # Interfaz frontend
│   └── requirements.txt         
├── entrenamiento/               # MÓDULO 2: Motor de Inteligencia Artificial
│   ├── entrenar_modelo.py       # Script de Transfer Learning y Fine-Tuning
│   └── graficas/                # Resultados de métricas (Accuracy, Loss, Matriz)
└── cana_saludable/              # MÓDULO 3: Aplicación Móvil (Flutter)
    ├── assets/                  # Modelo optimizado (modelo_cana_offline.tflite) e identidad visual
    ├── lib/main.dart            # Interfaz adaptativa, cámara e inferencia tensorial
    └── pubspec.yaml             # Dependencias del entorno móvil

```

---

## 🚀 Guías de Instalación y Ejecución

A continuación, se detalla cómo levantar cada uno de los módulos del proyecto:

### ⚙️ Módulo 1: Entrenamiento de la IA (Python)

Este módulo se encarga de procesar las imágenes, aplicar *Transfer Learning* (MobileNetV2) y ejecutar el Ajuste Fino (*Fine-Tuning*).

1. Abre tu terminal en la carpeta `/entrenamiento`.
2. Crea y activa un entorno virtual:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # En Windows PowerShell

```


3. Instala las dependencias matemáticas:
```bash
pip install tensorflow matplotlib seaborn scikit-learn

```


4. Ejecuta el entrenamiento (generará automáticamente el modelo `.tflite` y las gráficas):
```bash
python entrenar_modelo.py

```



### 🌐 Módulo 2: Aplicación Web (Flask)

1. Abre tu terminal en la carpeta `/web` (asegúrate de tener Python 3.10+).
2. Instala las dependencias del servidor:
```bash
pip install -r requirements.txt

```


3. Levanta el servidor Backend (procesamiento IA):
```bash
python app.py

```


4. En una terminal nueva, levanta el servidor Frontend:
```bash
python -m http.server 8080 

```


5. Accede desde tu navegador a `http://localhost:8080/`. *(Nota: Para usar la cámara web en producción fuera de localhost, se requiere configurar un certificado SSL/HTTPS).*

### 📱 Módulo 3: Aplicación Móvil Offline (Flutter)

Esta aplicación contiene el modelo comprimido y funciona de manera 100% local.

1. Abre tu terminal en la carpeta `/entrenamiento/cana_saludable/`.
2. Descarga las dependencias del framework (TensorFlow Lite Flutter, Image Picker):
```bash
flutter pub get

```


3. (Opcional) Si cambiaste la imagen `logo.png` en los *assets*, regenera los íconos del sistema:
```bash
dart run flutter_launcher_icons

```


4. Compila el instalador APK de producción:
```bash
flutter build apk --release

```


*El archivo final se ubicará en `build/app/outputs/flutter-apk/app-release.apk`, listo para ser transferido a cualquier dispositivo Android.*