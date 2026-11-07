import os

import numpy as np

from PIL import Image

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


router = APIRouter(
    prefix="/api/detection",
    tags=["Disaster Detection"]
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "disaster_model.keras"
)

CLASSES_PATH = os.path.join(
    BASE_DIR,
    "models",
    "classes.txt"
)


# ============================================================
# SETTINGS
# ============================================================

IMAGE_SIZE = 224


# ============================================================
# LOAD MODEL
# ============================================================

model = None
class_names = []


def load_disaster_model():

    global model
    global class_names


    if not os.path.exists(
        MODEL_PATH
    ):

        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )


    if not os.path.exists(
        CLASSES_PATH
    ):

        raise FileNotFoundError(
            f"Classes file not found: {CLASSES_PATH}"
        )


    model = load_model(
        MODEL_PATH
    )


    with open(
        CLASSES_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        class_names = [
            line.strip()
            for line in file
            if line.strip()
        ]


load_disaster_model()


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/status")
async def detection_status():

    return {
        "success": True,
        "model_loaded": model is not None,
        "classes": class_names
    }


# ============================================================
# PREDICT
# ============================================================

@router.post("/predict")
async def predict_disaster(
    image: UploadFile = File(...)
):

    if model is None:

        raise HTTPException(
            status_code=500,
            detail="Disaster model is not loaded."
        )


    if not image.filename:

        raise HTTPException(
            status_code=400,
            detail="No image selected."
        )


    try:

        # ----------------------------------------------------
        # READ UPLOADED FILE
        # ----------------------------------------------------

        contents = await image.read()


        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty."
            )


        # ----------------------------------------------------
        # PIL DECODE
        # ----------------------------------------------------

        from io import BytesIO

        image_object = Image.open(
            BytesIO(contents)
        )


        # Force complete decode
        image_object.load()


        # ----------------------------------------------------
        # RGB
        # ----------------------------------------------------

        image_object = image_object.convert(
            "RGB"
        )


        # ----------------------------------------------------
        # RESIZE
        # ----------------------------------------------------

        image_object = image_object.resize(
            (
                IMAGE_SIZE,
                IMAGE_SIZE
            )
        )


        # ----------------------------------------------------
        # NUMPY
        # ----------------------------------------------------

        array = np.asarray(
            image_object,
            dtype=np.float32
        )


        # ----------------------------------------------------
        # ADD BATCH
        # ----------------------------------------------------

        array = np.expand_dims(
            array,
            axis=0
        )


        # ----------------------------------------------------
        # MOBILENET PREPROCESSING
        # ----------------------------------------------------

        array = preprocess_input(
            array
        )


        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        predictions = model.predict(
            array,
            verbose=0
        )[0]


        predicted_index = int(
            np.argmax(predictions)
        )


        confidence = float(
            predictions[predicted_index]
        ) * 100


        disaster_type = class_names[
            predicted_index
        ]


        # ----------------------------------------------------
        # ALL PREDICTIONS
        # ----------------------------------------------------

        all_predictions = []


        for index, probability in enumerate(
            predictions
        ):

            if index >= len(class_names):
                continue


            all_predictions.append(
                {
                    "disaster_type":
                        class_names[index],

                    "confidence":
                        round(
                            float(probability) * 100,
                            2
                        )
                }
            )


        all_predictions.sort(
            key=lambda item:
                item["confidence"],
            reverse=True
        )


        return {

            "success": True,

            "filename":
                image.filename,

            "disaster_type":
                disaster_type,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "predictions":
                all_predictions[:5]
        }


    except HTTPException:
        raise


    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to analyze image: {str(error)}"
        )