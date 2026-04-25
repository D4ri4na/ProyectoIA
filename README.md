# 🌾 Sistema Inteligente de Diagnóstico Foliar para Caña de Azúcar

![Estado](https://img.shields.io/badge/Estado-Completado-success)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.12-yellow)
![Framework](https://img.shields.io/badge/Framework-Flask-black)

## 📌 Descripción del Proyecto
Este proyecto es una aplicación web impulsada por Inteligencia Artificial diseñada para automatizar la identificación de patologías foliares en cultivos de caña de azúcar (*Saccharum officinarum*). 

Desarrollado como solución tecnológica para la agroindustria del departamento de Santa Cruz, el sistema utiliza un modelo de clasificación automatizada entrenado con un banco híbrido de **2,523 imágenes reales**. El objetivo es proporcionar a los productores una primera línea de defensa tecnológica, mitigando la dependencia de inspecciones manuales y optimizando los tiempos de reacción ante brotes infecciosos.

## 🎯 Enfermedades Detectables
El modelo es capaz de clasificar hojas sanas y diagnosticar cuatro de las enfermedades de mayor impacto económico en la región:
1. **Hoja Sana (Control)**
2. **Roya** (*Puccinia*)
3. **Muermo Rojo** (*Colletotrichum*)
4. **Virus del Mosaico**
5. **Síndrome de la Hoja Amarilla**

*Precisión predictiva global validada: **94.53%***

## ⚙️ Arquitectura del Sistema
El proyecto sigue una arquitectura **Cliente-Servidor** separando la lógica de inferencia de la interfaz de usuario:

* **Backend (Python/Flask):** Orquesta la recepción de datos y la comunicación con el modelo de aprendizaje automático (`keras_model.h5`).
* **Modelo de IA:** Utiliza TensorFlow/Keras para procesar tensores de imágenes (224x224 px) y calcular las probabilidades de clasificación.
* **Frontend (HTML5/CSS/JS Vanilla):** Interfaz web minimalista e interactiva que permite a los usuarios cargar imágenes desde sus dispositivos o capturar fotografías en tiempo real mediante la cámara del navegador.

## 📁 Estructura del Repositorio
```text
/
├── app.py                # Servidor principal (Flask)
├── model_logic.py        # Clase que gestiona la carga y predicción de la IA
├── keras_model.h5        # Pesos y estructura del modelo entrenado
├── labels.txt            # Etiquetas de clasificación
├── requirements.txt      # Dependencias del proyecto
├── style.css             # Estilos de la aplicación web
├── app.js                # Lógica de cliente (Cámara y envíos asíncronos)
└── index.html            # Estructura de la interfaz
```

## 🚀 Guía de Instalación y Uso

### 1. Requisitos Previos
Asegúrate de tener instalado Python (versión recomendada 3.10+). Es aconsejable utilizar un entorno virtual.

### 2. Instalación de Dependencias
Abre tu terminal en la carpeta raíz del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```
*(Nota: Las librerías principales incluyen `flask`, `tensorflow`, `tf-keras`, `Pillow` y `numpy`).*

### 3. Ejecución del Servidor
Para iniciar la aplicación, ejecuta el siguiente comando:
```bash
python app.py
```

### 4. Acceso a la Interfaz
Una vez que la consola indique que el servidor está corriendo (generalmente en el puerto 5000), en otra terminal ejecuta el siguiente comando:
```bash
python -m http.server 8080 
```
Y en tu navegador busca http://localhost:8080/ para que te aparezca la interfaz

> **Aviso sobre el uso de la cámara:** Para probar la funcionalidad de captura en tiempo real, debes acceder mediante `localhost`. Si despliegas la aplicación en un servidor en la nube (ej. AWS EC2), requerirás configurar un certificado SSL (HTTPS) para que los navegadores permitan el acceso a la cámara web.

