import time
import requests
import os
import threading
import sys

import RPi.GPIO as GPIO

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from sensors.ultrasonic_sensor import UltrasonicSensor
from sensors.camera_sensor import CameraSensor
from sensors.ldr_sensor import LDRSensor
from ml_models.vehicle_classification_model import VehicleClassificationModel

from raspberry_pi.data_models.vehicle_type import VehicleType
from raspberry_pi.repositories.slot_repository import SlotRepository
from raspberry_pi.repositories.ticket_repository import TicketRepository
from raspberry_pi.services.slot_manager_service import SlotManagerService
from raspberry_pi.services.ticket_manager_service import TicketManagerService

from utils.logger_utils import entry_logger, exit_logger, light_logger, main_logger, log_both

CLOUD_API_URL = "http://35.200.128.215:8000"

ENTRY_POLL_INTERVAL = 1
EXIT_POLL_INTERVAL = 1
LIGHT_POLL_INTERVAL = 5

ENTRY_MIN_DISTANCE = 0
ENTRY_MAX_DISTANCE = 10

RESET_REQUIRED = 2


# ---------------- STATUS PUSH HELPER ----------------
def push_driver_status(status: str, message: str = "", ticket: dict = None):
    """Push a transient UI status to the cloud server state machine."""
    try:
        payload = {"status": status, "message": message, "ticket": ticket}
        requests.put(
            f"{CLOUD_API_URL}/driver-view/status",
            json=payload,
            timeout=5
        )
    except Exception as e:
        log_both(entry_logger, f"Failed to push driver status '{status}': {e}", level="warning")


# ---------------- ENTRY PROCESS ----------------
def entry_process(entry_sensor, camera, model, ticket_manager):
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

                # ── STATE: processing ──────────────────────────────────────
                push_driver_status("processing", "Recognizing vehicle, please wait...")

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
                    # ── STATE: error (camera failure) ──────────────────────
                    push_driver_status("error", "Camera error. Please contact staff.")
                    time.sleep(2)
                    continue

                vehicle_type_raw = model.classify_vehicle(img_path)
                log_both(entry_logger, f"Predicted vehicle type: {vehicle_type_raw}")
                local_path=camera.move_to_class_folder(vehicle_type_raw, img_path)
                send_image_to_cloud(local_path, vehicle_type_raw)

                

                try:
                    vehicle_type = VehicleType(vehicle_type_raw)
                except ValueError:
                    log_both(
                        entry_logger,
                        f"Invalid vehicle type predicted by model: {vehicle_type_raw}",
                        level="error"
                    )
                    # ── STATE: error (invalid vehicle) ────────────────────
                    push_driver_status("error", "Vehicle recognition failed. Please try again.")
                    time.sleep(2)
                    continue

                try:
                    log_both(entry_logger, "Allocating ticket locally on Raspberry Pi")
                    result = ticket_manager.allocate_ticket(vehicle_type)

                    if result.get("status") == "success":
                        log_both(entry_logger, f"Local ticket allocation success: {result}")
                        # ── STATE: success ─────────────────────────────────
                        push_driver_status("success", "", result)
                    else:
                        log_both(
                            entry_logger,
                            f"Local ticket allocation failed: {result}",
                            level="warning"
                        )
                        error_detail = result.get("message", "Ticket allocation failed.")
                        # ── STATE: error (local rejection) ─────────────────
                        push_driver_status("error", error_detail)

                except Exception as e:
                    log_both(entry_logger, f"Failed local ticket allocation: {e}", level="error")
                    # ── STATE: error (system failure) ─────────────────────
                    push_driver_status("error", "System error. Please try again.")

            elif not in_range and entry_seen:
                entry_seen = False
                log_both(entry_logger, "Entry zone cleared, sensor re-armed")

            time.sleep(ENTRY_POLL_INTERVAL)

        except Exception as e:
            log_both(entry_logger, f"Unexpected error in entry thread: {e}", level="error")
            # ── STATE: error (unexpected) ─────────────────────
            push_driver_status("error", "Unexpected error. Please try again.")
            time.sleep(2)


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
def exit_process(slot_sensor, slot_manager):
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
                            f"Processing slot release locally on Raspberry Pi for slot {current_slot}"
                        )

                        result = slot_manager.process_release_by_id(current_slot)

                        if result.get("status") in ("success", "ignored"):
                            log_both(exit_logger, f"Local release result: {result}")
                            last_triggered_slot = current_slot
                        else:
                            log_both(
                                exit_logger,
                                f"Local release failed: {result}",
                                level="error"
                            )

                    except Exception as e:
                        log_both(exit_logger, f"Failed local slot release: {e}", level="error")

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


def preload_local_memory(slot_repository, ticket_repository):
    """
    Best-effort preload so CSV fallback memory is seeded from Firestore at startup.
    If Firestore is unavailable, repositories will simply fall back internally.
    """
    try:
        slots = slot_repository.get_all_slots()
        log_both(main_logger, f"Preloaded slot memory with {len(slots)} slots")
    except Exception as e:
        log_both(main_logger, f"Failed to preload slot memory: {e}", level="warning")

    try:
        tickets = ticket_repository.get_all_tickets()
        log_both(main_logger, f"Preloaded ticket memory with {len(tickets)} tickets")
    except Exception as e:
        log_both(main_logger, f"Failed to preload ticket memory: {e}", level="warning")


# ---------------- MAIN ----------------
def main():
    entry_sensor = UltrasonicSensor(1, "Entry Sensor", 23, 24)
    slot_sensor = UltrasonicSensor(2, "Slot Sensor", 20, 21)
    camera = CameraSensor()
    ldr_sensor = LDRSensor()

    model_path = os.path.join(os.path.dirname(__file__), "ml_models", "vehicle_model_int8.tflite")
    model = VehicleClassificationModel(model_path)

    slot_repository = SlotRepository()
    ticket_repository = TicketRepository()

    preload_local_memory(slot_repository, ticket_repository)

    slot_manager = SlotManagerService(slot_repository)
    ticket_manager = TicketManagerService(ticket_repository, slot_manager)

    log_both(main_logger, "Raspberry Pi Edge Node Started")

    entry_thread = threading.Thread(
        target=entry_process,
        args=(entry_sensor, camera, model, ticket_manager),
        name="ENTRY-THREAD",
        daemon=True
    )

    exit_thread = threading.Thread(
        target=exit_process,
        args=(slot_sensor, slot_manager),
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
        GPIO.cleanup()


if __name__ == "__main__":
    main()