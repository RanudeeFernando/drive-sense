import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

class VehicleClassificationModel:
    """
    Loads a TensorFlow Lite model to classify vehicle types from images.
    Performs preprocessing, inference, and returns predicted vehicle class with confidence.
    """
    def __init__(self, model_path: str = "ml_models/vehicle_model_int8.tflite"):
        self.model_path = model_path
        self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def classify_vehicle(self, img_path: str) -> str:
        """
        Classifies a vehicle from the given image using a TFLite model.
        Returns the predicted vehicle type (bike, car, lorry, or unknown).
        """
        img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
        img_array = tf.keras.utils.img_to_array(img)
        img_array = preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)

        input_scale, input_zero_point = self.input_details[0]['quantization']

        if input_scale != 0:
            img_array = img_array / input_scale + input_zero_point
            img_array = np.round(img_array).astype(np.int8)

        self.interpreter.set_tensor(self.input_details[0]['index'], img_array)
        self.interpreter.invoke()

        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        output_scale, output_zero_point = self.output_details[0]['quantization']

        if output_scale != 0:
            output = (output.astype(np.float32) - output_zero_point) * output_scale

        classes = ["bike", "car", "lorry", "unknown"]
        result = classes[np.argmax(output)]
        confidence = round(output[0][np.argmax(output)] * 100, 2)

        print(f"Classified as: {result} (Confidence: {confidence}%)")
        return result
    
    