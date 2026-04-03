import time
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sensors.ultrasonic_sensor import UltrasonicSensor
from sensors.camera_sensor import CameraSensor
from raspberry_pi.sensors.ldr_sensor import LDRSensor
from ml_models.vehicle_classification_model import VehicleClassificationModel

CLOUD_API_URL = "http://127.0.0.1:8000"

def main():
    ultrasonic = UltrasonicSensor()
    camera = CameraSensor()
    ldr_sensor = LDRSensor()
    model_path = os.path.join(os.path.dirname(__file__), "ml_models", "vehicle_model.h5")
    model = VehicleClassificationModel(model_name=model_path)

    print(" Raspberry Pi Edge Node Started...")
    
    for i in range(2):
        print(f"\n--- Entry level ultrasonic sensor acitvated ---")
        if ultrasonic.detect_object_in_range():
            print(" Vehicle Arrived!")
            img_path = camera.capture_image()
            
            # Since the camera sensor dumps images to root, we might want to ensure they exist
            if not os.path.exists(img_path) and os.path.exists(os.path.join("..", img_path)):
                img_path = os.path.join("..", img_path)
            elif not os.path.exists(img_path):
                 print(f" Camera capture didn't generate {img_path}")
                 time.sleep(2)
                 continue

            vehicle_type = model.classify_vehicle(img_path)
            
            print(f"📡 Sending {vehicle_type} classification to cloud API...")
            try:
                response = requests.post(f"{CLOUD_API_URL}/ticketing", json={"vehicle_type": vehicle_type})
                if response.status_code == 200:
                    print(f" Cloud Response: {response.json()}")
                else:
                    print(f" Cloud Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f" Failed to reach cloud API: {e}")

        # Check for exiting vehicles
        print(f"--- Exit level ultrasonic sensor activated ---")
        if ultrasonic.detect_free_slot_by_distance() is not None:
            try:
                slot_id=ultrasonic.detect_free_slot_by_distance()
                print(f" Sending freed slot {slot_id} to cloud...")
                response = requests.post(f"{CLOUD_API_URL}/release_slot",json={"slot_id": slot_id})
                if response.status_code == 200:
                    print(f" Cloud Response: {response.json()}")
                else:                    
                    print(f" Cloud Error: {response.status_code} - {response.text}")   
            except Exception as e:
                print(f" Failed to reach cloud API: {e}")




        # Check light levels
        resistance = ldr_sensor.detect_light_level()
        print(f"--- LDR sensor: {resistance} Ω ---")
        try:
            light_resp = requests.post(f"{CLOUD_API_URL}/light", json={"resistance": resistance})
            if light_resp.status_code == 200:
                is_on = light_resp.json().get("light_on", False)
                if is_on:
                    print("💡 [PI RELAY] Turning LED ON!")
                else:
                    print("🌑 [PI RELAY] Turning LED OFF!")
            else:
                 print(f"❌ Cloud Error: {light_resp.status_code}")
        except Exception as e:
             print(f"❌ Failed to reach cloud API: {e}")
                 
        time.sleep(2)

if __name__ == "__main__":
    main()
