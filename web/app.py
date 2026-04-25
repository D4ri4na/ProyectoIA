import os
import io
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageOps

app = Flask(__name__)
CORS(app)

# ── Model state ──────────────────────────────────────────────────────────────
model = None
class_names = []
is_loaded = False

MODEL_PATH  = "keras_model.h5"
LABELS_PATH = "labels.txt"


def load_model_once():
    global model, class_names, is_loaded
    try:
        from tf_keras.models import load_model as keras_load
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"No se encontró '{MODEL_PATH}'.")
        if not os.path.exists(LABELS_PATH):
            raise FileNotFoundError(f"No se encontró '{LABELS_PATH}'.")

        model = keras_load(MODEL_PATH, compile=False)

        with open(LABELS_PATH, "r") as f:
            class_names = [line.strip() for line in f.readlines()]

        np.set_printoptions(suppress=True)
        is_loaded = True
        print("✅  Modelo cargado correctamente.")
    except Exception as e:
        print(f"❌  Error al cargar el modelo: {e}")
        is_loaded = False


def preprocess_image(pil_image: Image.Image) -> np.ndarray:
    """Resize, normalise and wrap in batch dim."""
    image = pil_image.convert("RGB")
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
    arr   = np.asarray(image, dtype=np.float32)
    arr   = (arr / 127.5) - 1.0
    return np.expand_dims(arr, axis=0)   # (1, 224, 224, 3)


def strip_index_prefix(name: str) -> str:
    """Remove leading '0 ', '1 ', … prefixes produced by Teachable Machine."""
    name = name.strip()
    if len(name) > 2 and name[1] == " ":
        return name[2:]
    return name


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"loaded": is_loaded})


@app.route("/predict", methods=["POST"])
def predict():
    if not is_loaded:
        return jsonify({"error": "El modelo aún no está cargado."}), 503

    # Accept either a multipart file upload or a base64 JSON body
    try:
        if "file" in request.files:
            file  = request.files["file"]
            image = Image.open(file.stream)
        elif request.is_json and "image" in request.json:
            # base64-encoded data-URL: "data:image/...;base64,<data>"
            data_url = request.json["image"]
            header, encoded = data_url.split(",", 1)
            image = Image.open(io.BytesIO(base64.b64decode(encoded)))
        else:
            return jsonify({"error": "No se recibió ninguna imagen."}), 400
    except Exception as e:
        return jsonify({"error": f"No se pudo leer la imagen: {e}"}), 400

    data       = preprocess_image(image)
    prediction = model.predict(data, verbose=0)
    index      = int(np.argmax(prediction))

    top_class   = strip_index_prefix(class_names[index])
    confidence  = float(prediction[0][index])

    breakdown = []
    for i, name in enumerate(class_names):
        breakdown.append({
            "label":       strip_index_prefix(name),
            "probability": float(prediction[0][i])
        })
    breakdown.sort(key=lambda x: x["probability"], reverse=True)

    return jsonify({
        "diagnosis":  top_class,
        "confidence": confidence,
        "breakdown":  breakdown
    })


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    load_model_once()
    app.run(host="0.0.0.0", port=5000, debug=False)