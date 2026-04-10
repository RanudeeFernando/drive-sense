import time
import requests
import os
import threading
import sys
import requests


# import RPi.GPIO as GPIO

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sensors.ultrasonic_sensor import UltrasonicSensor
from sensors.camera_sensor import CameraSensor
from sensors.ldr_sensor import LDRSensor
from ml_models.vehicle_classification_model import VehicleClassificationModel

CLOUD_API_URL = "http://35.200.128.215:8000"

ENTRY_POLL_INTERVAL = 1
EXIT_POLL_INTERVAL = 1
LIGHT_POLL_INTERVAL = 5

ENTRY_MIN_DISTANCE = 0
ENTRY_MAX_DISTANCE = 10

RESET_REQUIRED = 2

from utils.logger_utils import entry_logger, exit_logger, light_logger, main_logger, log_both



# import cv2
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# =========================
# CONFIG
# =========================
SERVICE_ACCOUNT_FILE = "credentials/serviceAccountKey.json"
FOLDER_ID = "YOUR_DRIVE_FOLDER_ID"

# =========================
# AUTHENTICATE DRIVE
# =========================
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive"]
)

drive_service = build('drive', 'v3', credentials=credentials)

def upload_to_drive(file_path):
    file_metadata = {
        'name': file_path,
        'parents': [FOLDER_ID]
    }

    media = MediaFileUpload(file_path, mimetype='image/jpeg')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')
    print("Uploaded to Drive. File ID:", file_id)

    return file_id

def make_public(file_id):
    drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view"

def send_to_backend(file_id, url):
    data = {
        "file_id": file_id,
        "file_url": url
    }

    response = requests.post(f"{CLOUD_API_URL}/upload", json=data)
    print("Backend response:", response.text)



# ---------------- ENTRY PROCESS ----------------
def entry_process(entry_sensor, camera, model):
    entry_seen = False

    while True:
        try:
            distance = entry_sensor.get_distance()

            if distance is None:
                time.sleep(ENTRY_POLL_INTERVAL)
                continue

            in_range = ENTRY_MIN_DISTANCE <= distance <= ENTRY_MAX_DISTANCE

            if in_range and not entry_seen:
                entry_seen = True
                log_both(entry_logger, f"Vehicle detected at entry: {distance} cm")

                img_path = camera.capture_image()
                log_both(entry_logger, f"Captured image path: {img_path}")

                if not os.path.exists(img_path) and os.path.exists(os.path.join("..", img_path)):
                    img_path = os.path.join("..", img_path)
                elif not os.path.exists(img_path):
                    log_both(
                        entry_logger,
                        f"Camera capture did not generate file: {img_path}",
                        level="warning"
                    )
                    time.sleep(2)
                    continue

                vehicle_type = model.classify_vehicle(img_path)
                # Move image into correct folder
                local_path = camera.move_to_class_folder(vehicle_type, img_path)
                # Send to cloud
                file_id = upload_to_drive(local_path)

                file_url = make_public(file_id)

                send_to_backend(file_id, file_url)
                # send_image_to_cloud(local_path, vehicle_type)
                log_both(entry_logger, f"Predicted vehicle type: {vehicle_type}")

                try:
                    log_both(entry_logger, "Sending ticket request to cloud")
                    response = requests.post(
                        f"{CLOUD_API_URL}/ticket",
                        json={"vehicle_type": vehicle_type},
                        timeout=5
                    )

                    if response.status_code == 200:
                        log_both(entry_logger, f"Cloud response: {response.json()}")
                    else:
                        log_both(
                            entry_logger,
                            f"Cloud error {response.status_code}: {response.text}",
                            level="error"
                        )

                except Exception as e:
                    log_both(entry_logger, f"Failed to reach cloud API: {e}", level="error")

            elif not in_range and entry_seen:
                entry_seen = False
                log_both(entry_logger, "Entry zone cleared, sensor re-armed")

            time.sleep(ENTRY_POLL_INTERVAL)

        except Exception as e:
            log_both(entry_logger, f"Unexpected error in entry thread: {e}", level="error")
            time.sleep(2)

# ---------------- Sending data to cloud ----------------
def send_image_to_cloud(image_path, vehicle_type):
    vehicle_type = vehicle_type.lower()

    if not os.path.exists(image_path):
        print(f"Image {image_path} not found")
        return

    files = {"file": open(image_path, "rb")}

    response = requests.post(
        f"{CLOUD_API_URL}/upload-image/{vehicle_type}",  
        files=files
    )

    if response.status_code == 200:
        print(f"Uploaded image to cloud: {response.json()}")
    else:
        print(f"Failed to upload image: {response.status_code} - {response.text}")



# ---------------- EXIT PROCESS ----------------
def exit_process(slot_sensor):
    last_triggered_slot = None
    reset_count = 0

    while True:
        try:
            distance = slot_sensor.get_distance()

            if distance is None:
                time.sleep(EXIT_POLL_INTERVAL)
                continue

            current_slot = slot_sensor.get_slot_id_by_distance(distance)

            if current_slot is not None:
                reset_count = 0

                if current_slot != last_triggered_slot:
                    log_both(
                        exit_logger,
                        f"Slot {current_slot} detected at {distance} cm"
                    )

                    try:
                        log_both(
                            exit_logger,
                            f"Sending release request for slot {current_slot} to cloud"
                        )
                        response = requests.post(
                            f"{CLOUD_API_URL}/release-slot",
                            json={"slot_id": current_slot},
                            timeout=5
                        )

                        if response.status_code == 200:
                            log_both(exit_logger, f"Cloud response: {response.json()}")
                            last_triggered_slot = current_slot
                        else:
                            log_both(
                                exit_logger,
                                f"Cloud error {response.status_code}: {response.text}",
                                level="error"
                            )

                    except Exception as e:
                        log_both(exit_logger, f"Failed to reach cloud API: {e}", level="error")

                # Still inside same slot range -> ignore silently

            else:
                if last_triggered_slot is not None:
                    reset_count += 1

                    if reset_count == 1:
                        log_both(
                            exit_logger,
                            f"Sensor left slot ranges, waiting to re-arm ({reset_count}/{RESET_REQUIRED})"
                        )

                    if reset_count >= RESET_REQUIRED:
                        log_both(
                            exit_logger,
                            "Exit sensor reset and re-armed"
                        )
                        last_triggered_slot = None
                        reset_count = 0

            time.sleep(EXIT_POLL_INTERVAL)

        except Exception as e:
            log_both(exit_logger, f"Unexpected error in exit thread: {e}", level="error")
            time.sleep(2)


# ---------------- LIGHTING PROCESS ----------------
def lighting_process(ldr_sensor):
    last_light_state = None
    last_enabled_state = None

    while True:
        try:
            try:
                status_resp = requests.get(f"{CLOUD_API_URL}/ldr-status", timeout=5)
                ldr_enabled = (
                    status_resp.json().get("enabled", True)
                    if status_resp.status_code == 200
                    else True
                )
            except Exception as e:
                log_both(light_logger, f"Failed to fetch LDR status: {e}", level="error")
                ldr_enabled = True

            if ldr_enabled != last_enabled_state:
                log_both(light_logger, f"LDR enabled state changed: {ldr_enabled}")
                last_enabled_state = ldr_enabled

            if ldr_enabled:
                resistance = ldr_sensor.read_resistance()
                light_status = ldr_sensor.is_light(resistance)
                ldr_sensor.control_led(light_status)

                if light_status != last_light_state:
                    log_both(
                        light_logger,
                        f"LDR resistance: {resistance} ohms | sending lighting update: {'ON' if light_status else 'OFF'}"
                    )

                    try:
                        response = requests.post(
                            f"{CLOUD_API_URL}/lighting",
                            json={"light_on": light_status},
                            timeout=5
                        )

                        if response.status_code == 200:
                            cloud_state = response.json().get("light_on", False)
                            log_both(
                                light_logger,
                                f"Cloud response: {'ON' if cloud_state else 'OFF'}"
                            )
                        else:
                            log_both(
                                light_logger,
                                f"Cloud error {response.status_code}: {response.text}",
                                level="error"
                            )

                    except Exception as e:
                        log_both(light_logger, f"Failed to reach cloud API: {e}", level="error")

                    last_light_state = light_status

            else:
                ldr_sensor.control_led(False)

            time.sleep(LIGHT_POLL_INTERVAL)

        except Exception as e:
            log_both(light_logger, f"Unexpected error in lighting thread: {e}", level="error")
            time.sleep(2)


# ---------------- MAIN ----------------
def main():
    entry_sensor = UltrasonicSensor(1, "entry sensor")
    slot_sensor = UltrasonicSensor(2, "slot sensor")
    camera = CameraSensor()
    ldr_sensor = LDRSensor()


    model_path = os.path.join(os.path.dirname(__file__), "ml_models", "vehicle_model_int8.tflite")
    model = VehicleClassificationModel(model_path)

    log_both(main_logger, "Raspberry Pi Edge Node Started")

    entry_thread = threading.Thread(
        target=entry_process,
        args=(entry_sensor, camera, model),
        name="ENTRY-THREAD",
        daemon=True
    )

    exit_thread = threading.Thread(
        target=exit_process,
        args=(slot_sensor,),
        name="EXIT-THREAD",
        daemon=True
    )

    light_thread = threading.Thread(
        target=lighting_process,
        args=(ldr_sensor,),
        name="LIGHT-THREAD",
        daemon=True
    )

    entry_thread.start()
    exit_thread.start()
    light_thread.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        log_both(main_logger, "Shutting down...")
        # GPIO.cleanup()


if __name__ == "__main__":
    main()