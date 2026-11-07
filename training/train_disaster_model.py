import os
import json
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_DIR = BASE_DIR / "dataset"
MODEL_DIR = BASE_DIR / "trained_model"

MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "disaster_model.keras"
CLASSES_PATH = MODEL_DIR / "classes.json"

IMAGE_SIZE = 224
BATCH_SIZE = 8
EPOCHS = 15

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".gif"
}


# ============================================================
# CHECK IMAGE
# ============================================================

def valid_image(path):

    try:

        with Image.open(path) as img:

            img.verify()

        return True

    except (
        UnidentifiedImageError,
        OSError,
        ValueError
    ):

        return False


# ============================================================
# CLEAN DATASET
# ============================================================

def scan_dataset():

    classes = sorted(
        [
            folder.name
            for folder in DATASET_DIR.iterdir()
            if folder.is_dir()
        ]
    )

    if not classes:

        raise RuntimeError(
            "No disaster folders found inside dataset/"
        )

    print("\nClasses found:")

    for cls in classes:
        print("  -", cls)

    valid_files = []
    invalid_files = []

    for class_name in classes:

        class_dir = DATASET_DIR / class_name

        for file in class_dir.rglob("*"):

            if not file.is_file():
                continue

            if file.suffix.lower() not in VALID_EXTENSIONS:

                invalid_files.append(file)
                continue

            if valid_image(file):

                valid_files.append(
                    (
                        str(file),
                        class_name
                    )
                )

            else:

                invalid_files.append(file)

    print(
        f"\nValid images   : {len(valid_files)}"
    )

    print(
        f"Invalid files  : {len(invalid_files)}"
    )

    if invalid_files:

        print("\nInvalid files:")

        for file in invalid_files:

            print("  ", file)

    if len(valid_files) == 0:

        raise RuntimeError(
            "No valid images found."
        )

    return classes, valid_files


# ============================================================
# LOAD IMAGES MANUALLY
# ============================================================

def load_images(classes, files):

    class_to_index = {
        name: index
        for index, name in enumerate(classes)
    }

    images = []
    labels = []

    for index, (file_path, class_name) in enumerate(files):

        try:

            image = Image.open(
                file_path
            ).convert("RGB")

            image = image.resize(
                (
                    IMAGE_SIZE,
                    IMAGE_SIZE
                )
            )

            array = np.asarray(
                image,
                dtype=np.float32
            )

            array /= 255.0

            images.append(array)

            labels.append(
                class_to_index[class_name]
            )

        except Exception as error:

            print(
                "Skipping:",
                file_path,
                error
            )

        if (index + 1) % 20 == 0:

            print(
                f"Loaded {index + 1}/{len(files)}"
            )

    X = np.array(
        images,
        dtype=np.float32
    )

    y = np.array(
        labels,
        dtype=np.int32
    )

    return X, y


# ============================================================
# TRAIN
# ============================================================

def train():

    print("\n==============================")
    print(" AI CP DISASTER MODEL TRAINING")
    print("==============================\n")

    classes, files = scan_dataset()

    X, y = load_images(
        classes,
        files
    )

    print(
        "\nDataset shape:",
        X.shape
    )

    print(
        "Labels shape:",
        y.shape
    )

    if len(X) < 10:

        raise RuntimeError(
            "Too few valid images. Add more images to your dataset."
        )

    # --------------------------------------------------------
    # Shuffle
    # --------------------------------------------------------

    indices = np.arange(
        len(X)
    )

    np.random.shuffle(
        indices
    )

    X = X[indices]
    y = y[indices]

    # --------------------------------------------------------
    # Validation split
    # --------------------------------------------------------

    split = int(
        len(X) * 0.8
    )

    if split <= 0 or split >= len(X):

        raise RuntimeError(
            "Not enough images for training/validation split."
        )

    X_train = X[:split]
    y_train = y[:split]

    X_val = X[split:]
    y_val = y[split:]

    print(
        "\nTraining images:",
        len(X_train)
    )

    print(
        "Validation images:",
        len(X_val)
    )

    # --------------------------------------------------------
    # Data augmentation
    # --------------------------------------------------------

    augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip(
                "horizontal"
            ),

            layers.RandomRotation(
                0.08
            ),

            layers.RandomZoom(
                0.10
            ),

            layers.RandomContrast(
                0.10
            )
        ]
    )

    # --------------------------------------------------------
    # MobileNetV2
    # --------------------------------------------------------

    base_model = MobileNetV2(
        include_top=False,
        weights="imagenet",
        input_shape=(
            IMAGE_SIZE,
            IMAGE_SIZE,
            3
        )
    )

    base_model.trainable = False

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    inputs = layers.Input(
        shape=(
            IMAGE_SIZE,
            IMAGE_SIZE,
            3
        )
    )

    x = augmentation(inputs)

    x = base_model(
        x,
        training=False
    )

    x = layers.GlobalAveragePooling2D()(x)

    x = layers.Dropout(
        0.30
    )(x)

    outputs = layers.Dense(
        len(classes),
        activation="softmax"
    )(x)

    model = models.Model(
        inputs,
        outputs
    )

    model.compile(

        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.0001
        ),

        loss="sparse_categorical_crossentropy",

        metrics=[
            "accuracy"
        ]
    )

    model.summary()

    # --------------------------------------------------------
    # Callbacks
    # --------------------------------------------------------

    callbacks = [

        tf.keras.callbacks.EarlyStopping(

            monitor="val_loss",

            patience=4,

            restore_best_weights=True
        ),

        tf.keras.callbacks.ModelCheckpoint(

            str(MODEL_PATH),

            monitor="val_accuracy",

            save_best_only=True
        )
    ]

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    model.fit(

        X_train,
        y_train,

        validation_data=(
            X_val,
            y_val
        ),

        epochs=EPOCHS,

        batch_size=BATCH_SIZE,

        callbacks=callbacks
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    model.save(
        MODEL_PATH
    )

    with open(
        CLASSES_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            classes,
            file,
            indent=4
        )

    print("\n==============================")
    print(" TRAINING COMPLETE")
    print("==============================")

    print(
        "\nModel:",
        MODEL_PATH
    )

    print(
        "Classes:",
        CLASSES_PATH
    )


if __name__ == "__main__":

    train()