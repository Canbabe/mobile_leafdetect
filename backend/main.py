
import json
import io
from pathlib import Path

import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from tensorflow import keras

app = FastAPI(
    title="Deteksi Penyakit Daun Bawang",
    description="API deteksi penyakit daun bawang secara real-time",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lokasi model dan label kelas
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "daunai_mobilenetv2.keras"
CLASS_PATH = BASE_DIR / "models" / "class_names.json"

IMAGE_SIZE = (224, 224)

# Memuat model dan label saat backend dijalankan
if not MODEL_PATH.is_file():
    raise FileNotFoundError(
        f"Model AI tidak ditemukan: {MODEL_PATH}"
    )

if not CLASS_PATH.is_file():
    raise FileNotFoundError(
        f"File label kelas tidak ditemukan: {CLASS_PATH}"
    )

model = keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r", encoding="utf-8") as file:
    CLASS_NAMES = json.load(file)


@app.get("/")
def root():
    return {
        "message": "API Deteksi Penyakit Daun Bawang berhasil dijalankan"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": "loaded",
        "classes": CLASS_NAMES
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    image_data = await file.read()

    try:
        # Membuka gambar dan mengubahnya menjadi RGB
        image = Image.open(io.BytesIO(image_data))
        image = image.convert("RGB")

        width, height = image.size

        # Menyesuaikan ukuran gambar dengan input model
        image = image.resize(IMAGE_SIZE)

        # Mengubah gambar menjadi array
        image_array = np.asarray(image, dtype=np.float32)

        # Preprocessing yang sama seperti saat training
        image_array = keras.applications.mobilenet_v2.preprocess_input(
            image_array
        )

        # Menambahkan dimensi batch
        image_array = np.expand_dims(image_array, axis=0)

        # Prediksi kelas
        predictions = model.predict(image_array, verbose=0)[0]

        predicted_index = int(np.argmax(predictions))
        disease = CLASS_NAMES[predicted_index]
        confidence = float(predictions[predicted_index])

        return {
            "status": "success",
            "disease": disease,
            "confidence": round(confidence, 4),
            "confidence_percent": round(confidence * 100, 2),
            "image_size": {
                "width": width,
                "height": height
            },
            "predictions": {
                name: round(float(score), 4)
                for name, score in zip(CLASS_NAMES, predictions)
            }
        }

    except (UnidentifiedImageError, OSError, ValueError):
        return {
            "status": "error",
            "message": "File bukan gambar yang valid"
        }
