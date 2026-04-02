import os
import cv2
import numpy as np

# Try to import tensorflow, but don't crash the whole app if it's not installed yet
try:
    import tensorflow as tf
except ImportError:
    tf = None

class VehicleClassificationModel:
    def __init__(self, model_path="models/vehicle_classifier_model.h5"):
        self.model_path = model_path
        self.model = None
        
        # NOTE: Update these variables based on how you trained your specific .h5 model
        self.input_shape = (224, 224) 
        self.class_names = ["bike", "car", "lorry"] # Ensure this matches your model's classification output order!

    def get_model_name(self):
        return self.model_path

    def set_model_name(self, model_path):
        self.model_path = model_path

    def load_model(self):
        print(f"Loading model: {self.model_path}")
        
        # Resolve the absolute path assuming models/ is in the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        abs_model_path = os.path.join(project_root, self.model_path)
        
        if not os.path.exists(abs_model_path):
            print(f"Warning: Model file '{abs_model_path}' not found. Using mock behavior.")
            return

        if tf is None:
            print("Warning: TensorFlow is not installed. Using mock behavior. Please run 'pip install tensorflow'")
            return
            
        print(f"Model file '{abs_model_path}' found! Loading Keras .h5 model...")
        try:
            self.model = tf.keras.models.load_model(abs_model_path)
            print("TensorFlow model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")

    def classify_vehicle(self, image_path):
        if self.model is None or tf is None:
            # Fallback mock classifier if model is missing
            return "car"

        print(f"Classifying {image_path} with loaded .h5 model...")
        try:
            # Preprocess the grabbed camera image
            img = cv2.imread(image_path)
            if img is None:
                print("Error reading captured image file.")
                return "car"

            # Resize to expected input shape (e.g., 224x224)
            img_resized = cv2.resize(img, self.input_shape)
            
            # Convert to RGB (OpenCV uses BGR by default, models usually train on RGB)
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            
            # MobileNetV2 specific preprocessing: scales pixels from [0, 255] to [-1, 1]
            if tf is not None:
                img_normalized = tf.keras.applications.mobilenet_v2.preprocess_input(img_rgb)
            else:
                img_normalized = img_rgb / 127.5 - 1.0 # fallback math
            
            # Add batch dimension: shape becomes (1, 224, 224, 3)
            img_batch = np.expand_dims(img_normalized, axis=0)

            
            # Pass into the model prediction engine
            predictions = self.model.predict(img_batch, verbose=0)
            
            # Get the class with the highest probability
            predicted_index = np.argmax(predictions, axis=1)[0]
            predicted_class = self.class_names[predicted_index]
            
            print(f"Prediction probabilities: {predictions} -> Mapped to: {predicted_class}")
            return predicted_class
            
        except Exception as e:
            print(f"Error classifying image: {e}")
            return "car"