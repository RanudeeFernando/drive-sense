import time
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sensors.ultrasonic_sensor import UltrasonicSensor
from sensors.camera_sensor import CameraSensor
from sensors.ldr_sensor import LDRSensor
from ml_models.vehicle_classification_model import VehicleClassificationModel

CLOUD_API_URL = "http://34.100.218.79:8000"

def main():
    entry_sensor = UltrasonicSensor(
        sensor_id=1,
        name="Entry Sensor",
        trig_pin=16,
        echo_pin=18
    )

    slot_sensor = UltrasonicSensor(
        sensor_id=2,
        name="Slot Sensor",
        trig_pin=22,
        echo_pin=24
    )
    camera = CameraSensor()
    ldr_sensor = LDRSensor()
    model_path = os.path.join(os.path.dirname(__file__), "ml_models", "vehicle_model_int8.tflite")
    model = VehicleClassificationModel(model_path)

    print(" Raspberry Pi Edge Node Started...")
    
    for i in range(2):
        print(f"\n--- Entry level ultrasonic sensor acitvated ---")
        if entry_sensor.detect_object_in_range():
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
            
            print(f" Sending {vehicle_type} classification to cloud API...")
            try:
                response = requests.post(f"{CLOUD_API_URL}/ticket", json={"vehicle_type": vehicle_type})
                if response.status_code == 200:
                    print(f" Cloud Response: {response.json()}")
                else:
                    print(f" Cloud Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f" Failed to reach cloud API: {e}")

        # Check for exiting vehicles
        print(f"--- Exit level ultrasonic sensor activated ---")
        distance = slot_sensor.get_distance()
        if distance is not None:
            try:
                print(f"Sending exit distance {distance} to cloud...")
                response = requests.post(
                    f"{CLOUD_API_URL}/release-slot",
                    json={"distance": distance}
                )
                if response.status_code == 200:
                    print(f"Cloud Response: {response.json()}")
                else:
                    print(f"Cloud Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Failed to reach cloud API: {e}")

        # Check light levels
        resistance = ldr_sensor.read_resistance()
        print(f"--- LDR sensor: {resistance} Ω ---")

        light_status = ldr_sensor.is_light(resistance)
        ldr_sensor.control_led(light_status)

        try:
            light_resp = requests.post(
                f"{CLOUD_API_URL}/lighting",
                json={"light_on": light_status}
            )

            if light_resp.status_code == 200:
                is_on = light_resp.json().get("light_on", False)
                if is_on:
                    print(" [PI RELAY] Turning LED ON!")
                else:
                    print(" [PI RELAY] Turning LED OFF!")
            else:
                print(f" Cloud Error: {light_resp.status_code}")

        except Exception as e:
            print(f" Failed to reach cloud API: {e}")

        time.sleep(2)

if __name__ == "__main__":
    main()
