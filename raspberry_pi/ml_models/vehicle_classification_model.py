import numpy as np # type: ignore
import tensorflow as tf # type: ignore


class VehicleClassificationModel:
    def __init__(self, model_name: str = "vehicle_model.h5"):
        self.model_name = model_name
        self.model = tf.keras.models.load_model(self.model_name, compile=False) 

    def get_model_name(self) -> str:
        return self.model_name

    def set_model_name(self, model_name: str) -> None:
        self.model_name = model_name

    def classify_vehicle(self, img_path: str) -> str:  
        img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
        img_array = tf.keras.utils.img_to_array(img)

        # normalize (very important if model expects it)
        img_array = img_array / 255.0

        img_array = np.expand_dims(img_array, axis=0)

        prediction = self.model.predict(img_array)

        classes = ["bike", "car", "lorry"]
        result = classes[np.argmax(prediction)]
        confidence = round(prediction[0][np.argmax(prediction)] * 100)

        print(f"🔍 Classified as: {result} (Confidence: {confidence:.2f})")
        return result