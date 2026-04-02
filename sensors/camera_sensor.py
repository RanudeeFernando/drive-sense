from sensors.sensor import Sensor
import cv2
import os
import time
import random

class CameraSensor(Sensor):
    def __init__(self, sensor_id, camera_index=0):
        super().__init__(sensor_id)
        self.camera_index = camera_index
        # Verify camera is accessible
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"Warning: Could not open camera {self.camera_index}")
        cap.release()

    def _get_random_dummy_image(self):
        dummy_dir = "dummy_images"
        if os.path.exists(dummy_dir):
            images = [f for f in os.listdir(dummy_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                chosen = random.choice(images)
                print(f"Using dummy image: {chosen}")
                return os.path.join(dummy_dir, chosen)
        return "dummy_vehicle_image.jpg"

    def capture_image(self):
        print(f"Activating camera {self.camera_index}...")
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            print("Error: Could not access the camera. Using random dummy image.")
            return self._get_random_dummy_image()
            
        # Allow the camera to warm up
        time.sleep(1)
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Ensure an output directory exists
            os.makedirs("captured_images", exist_ok=True)
            timestamp = int(time.time())
            filename = f"captured_images/vehicle_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Image successfully captured: {filename}")
            return filename
        else:
            print("Error: Could not read frame from camera. Using random dummy image.")
            return self._get_random_dummy_image()