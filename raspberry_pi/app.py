import time
import requests
import os
import threading
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sensors.ultrasonic_sensor import UltrasonicSensor
from sensors.camera_sensor import CameraSensor
from sensors.ldr_sensor import LDRSensor
from ml_models.vehicle_classification_model import VehicleClassificationModel

CLOUD_API_URL = "http://34.100.218.79:8000"


def entry_process(entry_sensor, camera, model):
    while True:
        print("\n--- Entry Sensor Checking ---")
        if entry_sensor.detect_object_in_range():
            print("Vehicle Arrived!")
            img_path = camera.capture_image()

            if not os.path.exists(img_path) and os.path.exists(os.path.join("..", img_path)):
                img_path = os.path.join("..", img_path)
            elif not os.path.exists(img_path):
                print(f"Camera capture didn't generate {img_path}")
                time.sleep(2)
                continue

            vehicle_type = model.classify_vehicle(img_path)
            print(f"Sending {vehicle_type} to cloud...")

            try:
                response = requests.post(
                    f"{CLOUD_API_URL}/ticket",
                    json={"vehicle_type": vehicle_type}
                )
                print(response.json())
            except Exception as e:
                print(f"Cloud API Error: {e}")

        time.sleep(1)


def exit_process(slot_sensor):
    while True:
        print("--- Exit Sensor Checking ---")
        distance = slot_sensor.get_distance()
        print(f"Slot Sensor Distance: {distance} cm")
        if distance is not None:
            try:
                response = requests.post(
                    f"{CLOUD_API_URL}/release-slot",
                    json={"distance": distance}
                )
                print(response.json())
            except Exception as e:
                print(f"Cloud API Error: {e}")

        time.sleep(1)


def lighting_process(ldr_sensor):
    while True:
        resistance = ldr_sensor.read_resistance()
        light_status = ldr_sensor.is_light(resistance)
        ldr_sensor.control_led(light_status)

        try:
            response = requests.post(
                f"{CLOUD_API_URL}/lighting",
                json={"light_on": light_status}
            )
            print(response.json())
        except Exception as e:
            print(f"Cloud API Error: {e}")

        time.sleep(5)


def main():
    entry_sensor = UltrasonicSensor(1, "Entry Sensor", 20, 21)
    slot_sensor = UltrasonicSensor(2, "Slot Sensor", 23, 24)
    camera = CameraSensor()
    ldr_sensor = LDRSensor()

    model_path = os.path.join(os.path.dirname(__file__), "ml_models", "vehicle_model_int8.tflite")
    model = VehicleClassificationModel(model_path)

    print("Raspberry Pi Edge Node Started...")

    # Create Threads
    entry_thread = threading.Thread(target=entry_process, args=(entry_sensor, camera, model))
    exit_thread = threading.Thread(target=exit_process, args=(slot_sensor,))
    light_thread = threading.Thread(target=lighting_process, args=(ldr_sensor,))

    # Start Threads
    entry_thread.start()
    exit_thread.start()
    light_thread.start()

    # Keep Main Thread Alive
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()