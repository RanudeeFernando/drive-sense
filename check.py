import tensorflow as tf # type: ignore

model = tf.keras.models.load_model("v.h5", compile=False)
print("Model loaded successfully!")

# Check the output layer
output_layer = model.layers[-1]
print("Output layer:", output_layer)

# Number of classes
num_classes = output_layer.units  # for Dense layer
print("Number of classes:", num_classes)

import tensorflow as tf # type: ignore
import numpy as np # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore

# Load your model
model = tf.keras.models.load_model("v.h5", compile=False)

# Define your class names (must match training)
class_names = ["bike", "car", "lorry"]

import tensorflow as tf # type: ignore
import numpy as np # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore

# Load your model
model = tf.keras.models.load_model("v.h5", compile=False)

# Class names (must match your training)
class_names = ["bike", "car", "lorry"]

# Images to predict
image_files = ["green.jpeg", "blue.jpeg", "white.jpeg", "yellow.jpeg"]

# Table header
print(f"{'Image':<10} | {'Class':<10} | {'Confidence':<10}")
print("-" * 35)

for img_path in image_files:
    # Load and preprocess
    img = image.load_img(img_path, target_size=(224, 224))  # adjust size to your model
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0  # normalize if your model was trained on normalized images

    # Predict
    pred = model.predict(x)
    pred_class_idx = np.argmax(pred, axis=1)[0]
    confidence = pred[0][pred_class_idx]

    # Print in table format
    print(f"{img_path:<10} | {class_names[pred_class_idx]:<10} | {confidence*100:>7.2f}%")