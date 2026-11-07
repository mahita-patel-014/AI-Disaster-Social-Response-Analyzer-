import json
from pathlib import Path
from io import BytesIO

import numpy as np
from PIL import (
    Image,
    ImageOps,
    UnidentifiedImageError
)

import tensorflow as tf


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


# ============================================================
# TRAINED MODEL
# ============================================================

MODEL_PATH = (
    BASE_DIR
    / "trained_model"
    / "disaster_model.keras"
)

CLASSES_PATH = (
    BASE_DIR
    / "trained_model"
    / "classes.json"
)


# ============================================================
# MODEL SETTINGS
# ============================================================

IMAGE_SIZE = 224


# ============================================================
# CACHE
# ============================================================

_model = None
_classes = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    global _model
    global _classes

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    if _model is None:

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                "Trained disaster model was not found.\n"
                f"Expected:\n{MODEL_PATH}"
            )

        try:

            print("\nLoading disaster AI model...")

            _model = tf.keras.models.load_model(
                MODEL_PATH,
                compile=False
            )

            print(
                f"Model loaded successfully: "
                f"{MODEL_PATH}"
            )

        except Exception as error:

            raise RuntimeError(
                "Failed to load disaster_model.keras.\n"
                f"Error: {error}"
            ) from error


    # --------------------------------------------------------
    # LOAD CLASSES
    # --------------------------------------------------------

    if _classes is None:

        if not CLASSES_PATH.exists():

            raise FileNotFoundError(
                "classes.json was not found.\n"
                f"Expected:\n{CLASSES_PATH}"
            )

        try:

            with open(
                CLASSES_PATH,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except Exception as error:

            raise RuntimeError(
                "Failed to read classes.json.\n"
                f"Error: {error}"
            ) from error


        # ----------------------------------------------------
        # LIST
        # ----------------------------------------------------

        if isinstance(data, list):

            _classes = [
                str(item).strip()
                for item in data
                if str(item).strip()
            ]


        # ----------------------------------------------------
        # DICTIONARY
        # ----------------------------------------------------

        elif isinstance(data, dict):

            numeric_items = []

            for key, value in data.items():

                try:

                    numeric_items.append(
                        (
                            int(key),
                            str(value).strip()
                        )
                    )

                except (ValueError, TypeError):

                    pass


            if numeric_items:

                numeric_items.sort(
                    key=lambda x: x[0]
                )

                _classes = [
                    value
                    for _, value in numeric_items
                    if value
                ]

            else:

                _classes = [
                    str(value).strip()
                    for value in data.values()
                    if str(value).strip()
                ]

        else:

            raise RuntimeError(
                "classes.json must contain "
                "a list or dictionary."
            )


    # --------------------------------------------------------
    # VALIDATE CLASSES
    # --------------------------------------------------------

    if not _classes:

        raise RuntimeError(
            "No disaster classes found."
        )


    # --------------------------------------------------------
    # MODEL OUTPUT
    # --------------------------------------------------------

    try:

        output_shape = _model.output_shape

        if isinstance(
            output_shape,
            list
        ):

            output_shape = output_shape[0]

        output_count = int(
            output_shape[-1]
        )

    except Exception as error:

        raise RuntimeError(
            "Unable to determine model output size."
        ) from error


    # --------------------------------------------------------
    # MODEL / CLASS MATCH
    # --------------------------------------------------------

    if output_count != len(_classes):

        raise RuntimeError(

            "MODEL / CLASS MISMATCH\n\n"

            f"Model outputs: {output_count}\n"
            f"Classes: {len(_classes)}\n"
            f"Classes: {_classes}"
        )


    print(
        "\n========================================"
    )

    print(
        "DISASTER AI MODEL READY"
    )

    print(
        "========================================"
    )

    print(
        "Classes:",
        _classes
    )

    print(
        "Input:",
        f"{IMAGE_SIZE} x {IMAGE_SIZE}"
    )

    print(
        "Output classes:",
        output_count
    )

    print(
        "========================================\n"
    )


    return _model, _classes


# ============================================================
# PREPARE IMAGE
# ============================================================

def prepare_image(image_bytes: bytes):

    if not image_bytes:

        raise ValueError(
            "Uploaded image is empty."
        )


    # --------------------------------------------------------
    # OPEN IMAGE
    # --------------------------------------------------------

    try:

        image = Image.open(
            BytesIO(image_bytes)
        )

        image.load()

    except (
        UnidentifiedImageError,
        OSError,
        ValueError
    ) as error:

        raise ValueError(
            "Uploaded file is not a valid image."
        ) from error


    # --------------------------------------------------------
    # FIX ORIENTATION
    # --------------------------------------------------------

    try:

        image = ImageOps.exif_transpose(
            image
        )

    except Exception:

        pass


    # --------------------------------------------------------
    # RGB
    # --------------------------------------------------------

    try:

        image = image.convert(
            "RGB"
        )

    except Exception as error:

        raise ValueError(
            "Unable to convert image to RGB."
        ) from error


    # --------------------------------------------------------
    # RESIZE
    # --------------------------------------------------------

    image = image.resize(
        (
            IMAGE_SIZE,
            IMAGE_SIZE
        ),
        Image.Resampling.LANCZOS
    )


    # --------------------------------------------------------
    # NUMPY
    # --------------------------------------------------------

    array = np.asarray(
        image,
        dtype=np.float32
    )


    # --------------------------------------------------------
    # NORMALIZATION
    #
    # MUST MATCH TRAINING
    # --------------------------------------------------------

    array = array / 255.0


    # --------------------------------------------------------
    # CHECK SHAPE
    # --------------------------------------------------------

    if array.shape != (
        IMAGE_SIZE,
        IMAGE_SIZE,
        3
    ):

        raise ValueError(
            f"Unexpected image shape: {array.shape}"
        )


    # --------------------------------------------------------
    # BATCH
    # --------------------------------------------------------

    return np.expand_dims(
        array,
        axis=0
    )


# ============================================================
# CONVERT OUTPUT TO PROBABILITIES
# ============================================================

def convert_to_probabilities(
    predictions
):

    predictions = np.asarray(
        predictions,
        dtype=np.float32
    )


    predictions = np.nan_to_num(
        predictions,
        nan=0.0,
        posinf=0.0,
        neginf=0.0
    )


    # --------------------------------------------------------
    # If values already look like probabilities
    # --------------------------------------------------------

    if (
        np.all(predictions >= 0)
        and
        np.all(predictions <= 1)
        and
        np.isclose(
            np.sum(predictions),
            1.0,
            atol=0.01
        )
    ):

        total = np.sum(predictions)

        if total > 0:

            return predictions / total


    # --------------------------------------------------------
    # Otherwise treat output as logits
    # --------------------------------------------------------

    return tf.nn.softmax(
        predictions
    ).numpy()


# ============================================================
# PREDICT DISASTER
# ============================================================

def predict_disaster(
    image_bytes: bytes
):

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if not isinstance(
        image_bytes,
        bytes
    ):

        raise ValueError(
            "Image data must be bytes."
        )


    if not image_bytes:

        raise ValueError(
            "Uploaded image is empty."
        )


    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    image_array = prepare_image(
        image_bytes
    )


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model, classes = load_model()


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    try:

        output = model.predict(
            image_array,
            verbose=0
        )

    except Exception as error:

        raise RuntimeError(
            "Disaster model prediction failed.\n"
            f"Error: {error}"
        ) from error


    # --------------------------------------------------------
    # NUMPY
    # --------------------------------------------------------

    try:

        predictions = np.asarray(
            output,
            dtype=np.float32
        )

    except Exception as error:

        raise RuntimeError(
            "Invalid model output."
        ) from error


    # --------------------------------------------------------
    # CHECK
    # --------------------------------------------------------

    if predictions.ndim != 2:

        raise RuntimeError(
            "Unexpected prediction shape: "
            f"{predictions.shape}"
        )


    if predictions.shape[0] < 1:

        raise RuntimeError(
            "Model returned no prediction."
        )


    predictions = predictions[0]


    # --------------------------------------------------------
    # CLASS COUNT
    # --------------------------------------------------------

    if len(predictions) != len(classes):

        raise RuntimeError(
            "Prediction/class mismatch.\n"
            f"Predictions: {len(predictions)}\n"
            f"Classes: {len(classes)}"
        )


    # --------------------------------------------------------
    # PROBABILITIES
    # --------------------------------------------------------

    predictions = convert_to_probabilities(
        predictions
    )


    # --------------------------------------------------------
    # BEST CLASS
    # --------------------------------------------------------

    best_index = int(
        np.argmax(
            predictions
        )
    )


    disaster_type = str(
        classes[best_index]
    ).strip()


    confidence = float(
        predictions[best_index] * 100
    )


    # --------------------------------------------------------
    # ALL PREDICTIONS
    # --------------------------------------------------------

    all_predictions = []

    for index, probability in enumerate(
        predictions
    ):

        all_predictions.append({

            "disaster":
                str(
                    classes[index]
                ).strip(),

            "confidence":
                round(
                    float(
                        probability * 100
                    ),
                    2
                )
        })


    all_predictions.sort(
        key=lambda item:
            item["confidence"],
        reverse=True
    )


    # --------------------------------------------------------
    # TERMINAL RESULT
    # --------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "DISASTER PREDICTION"
    )

    print(
        "========================================"
    )

    print(
        "Disaster:",
        disaster_type
    )

    print(
        "Confidence:",
        f"{confidence:.2f}%"
    )

    print(
        "========================================\n"
    )


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "disaster_type":
            disaster_type,

        "confidence":
            round(
                confidence,
                2
            ),

        "predictions":
            all_predictions
    }