import os
import shutil
import zipfile
import numpy as np
import tensorflow as tf
import gdown
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# CONFIG
# =========================
DATASET_ZIP_PATH = "model_train/dataset.zip"
BASE_DATASET_DIR = "cloud_server/model_train/dataset"
SPLIT_BASE_DIR = "cloud_server/model_train/split_dataset"
CLASSES = ["bike", "car", "lorry", "unknown"]

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10

MODEL_PATH = "cloud_server/model_train/vehicle_model.h5"
TFLITE_PATH = "cloud_server/model_train/vehicle_model_int8.tflite"
REPORTS_DIR = "cloud_server/model_train/reports"

# =========================
# DOWNLOAD DATASET
# =========================
def download_dataset():
    print("Downloading dataset from Google Drive...")

    folder_id = "1bV0oOqbcMOPoO0HN83WwoYvgxzxSOEke"

    os.makedirs("model_train", exist_ok=True)

    gdown.download_folder(
        id=folder_id,
        output="model_train",
        quiet=False,
        use_cookies=False
    )

    print("Download complete")


# =========================
# DATA SPLITTING
# =========================
def prepare_dataset():
    print("Preparing dataset...")

    zip_files = [f for f in os.listdir("model_train") if f.endswith('.zip')]
    if not zip_files:
        raise FileNotFoundError("No zip files found after download.")

    # Sort by modification time descending (latest first)
    zip_files.sort(key=lambda x: os.path.getmtime(os.path.join("model_train", x)), reverse=True)
    zip_path = os.path.join("model_train", zip_files[0])
    print(f"Using latest zip: {zip_path}")

    if os.path.exists(BASE_DATASET_DIR):
        shutil.rmtree(BASE_DATASET_DIR)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(BASE_DATASET_DIR)
        
    # Fix nested dataset issue
    nested_dir = os.path.join(BASE_DATASET_DIR, "dataset")
    if os.path.exists(nested_dir):
        for item in os.listdir(nested_dir):
            shutil.move(os.path.join(nested_dir, item), os.path.join(BASE_DATASET_DIR, item))
        os.rmdir(nested_dir)

    print("Extraction complete.")

    train_dir = os.path.join(SPLIT_BASE_DIR, "train")
    val_dir = os.path.join(SPLIT_BASE_DIR, "val")
    test_dir = os.path.join(SPLIT_BASE_DIR, "test")

    if os.path.exists(SPLIT_BASE_DIR):
        shutil.rmtree(SPLIT_BASE_DIR)

    os.makedirs(train_dir)
    os.makedirs(val_dir)
    os.makedirs(test_dir)

    for cls in CLASSES:
        cls_path = os.path.join(BASE_DATASET_DIR, cls)

        if not os.path.exists(cls_path):
            raise ValueError(f"Missing class folder: {cls_path}")

        images = [f for f in os.listdir(cls_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

        train_val, test = train_test_split(images, test_size=0.2, random_state=42)
        train, val = train_test_split(train_val, test_size=0.2, random_state=42)

        for folder, imgs in zip([train_dir, val_dir, test_dir], [train, val, test]):
            cls_folder = os.path.join(folder, cls)
            os.makedirs(cls_folder, exist_ok=True)

            for img in imgs:
                shutil.copy(os.path.join(cls_path, img), os.path.join(cls_folder, img))

    print("Dataset split complete")
    return train_dir, val_dir, test_dir


# =========================
# DATA GENERATORS
# =========================
def create_generators(train_dir, val_dir, test_dir):
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=30,
        zoom_range=0.25,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.15,
        horizontal_flip=True,
        brightness_range=[0.7, 1.3],
        fill_mode='nearest'
    )

    val_test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    train_gen = train_datagen.flow_from_directory(
        train_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='categorical'
    )

    val_gen = val_test_datagen.flow_from_directory(
        val_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='categorical'
    )

    test_gen = val_test_datagen.flow_from_directory(
        test_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='categorical', shuffle=False
    )

    return train_gen, val_gen, test_gen


# =========================
# MODEL BUILDING
# =========================
def build_model(num_classes):
    base_model = MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
        alpha=0.35
    )

    base_model.trainable = True

    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.05)),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.01),
        metrics=['accuracy']
    )

    return model


# =========================
# TRAINING
# =========================
def train_model(model, train_gen, val_gen):
    print("Training model...")
    history = model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS)
    return history


# =========================
# EVALUATION
# =========================
def evaluate_model(model, test_gen):
    print("Evaluating model...")

    loss, acc = model.evaluate(test_gen)
    print(f"Test Accuracy: {acc*100:.2f}%")

    y_true = test_gen.classes
    y_pred = np.argmax(model.predict(test_gen), axis=-1)

    print(classification_report(y_true, y_pred, target_names=test_gen.class_indices.keys()))

    cm = confusion_matrix(y_true, y_pred)

    # Save Heatmap
    os.makedirs(REPORTS_DIR, exist_ok=True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=test_gen.class_indices.keys(),
                yticklabels=test_gen.class_indices.keys())
    plt.title('Confusion Matrix Heatmap')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    heatmap_path = os.path.join(REPORTS_DIR, "heatmap.png")
    plt.savefig(heatmap_path)
    plt.close()
    print(f"Heatmap saved to: {heatmap_path}")

# =========================
# QUANTIZATION
# =========================
def quantize_model(model, train_gen):
    print("Quantizing model...")

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    def representative_data_gen():
        for _ in range(100):
            images, _ = next(train_gen)
            yield [images.astype(np.float32)]

    converter.representative_dataset = representative_data_gen
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()

    with open(TFLITE_PATH, "wb") as f:
        f.write(tflite_model)

    print("Quantized model saved:", TFLITE_PATH)


# =========================
# MAIN PIPELINE
# =========================
def main():
    try:
        download_dataset()
        train_dir, val_dir, test_dir = prepare_dataset()
        train_gen, val_gen, test_gen = create_generators(train_dir, val_dir, test_dir)

        model = build_model(train_gen.num_classes)

        train_model(model, train_gen, val_gen)
        evaluate_model(model, test_gen)

        model.save(MODEL_PATH)
        print("Model saved:", MODEL_PATH)

        quantize_model(model, train_gen)

    finally:
        if os.path.exists(SPLIT_BASE_DIR):
            shutil.rmtree(SPLIT_BASE_DIR)

        if os.path.exists(BASE_DATASET_DIR):
            shutil.rmtree(BASE_DATASET_DIR)

        # Remove all zip files
        if os.path.exists("model_train"):
            for f in os.listdir("model_train"):
                if f.endswith('.zip'):
                    os.remove(os.path.join("model_train", f))

if __name__ == "__main__":
    main()