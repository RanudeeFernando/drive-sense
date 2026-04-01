# app.py

import time

from sensors.ultrasonic_sensor import UltrasonicSensor
from sensors.camera_sensor import CameraSensor
from ml_models.vehicle_classification_model import VehicleClassificationModel
from data_models.parking_slot import ParkingSlot
from data_models.ticket import Ticket
from controller.entry_controller import EntryController
import tensorflow as tf # type: ignore
from controller.exit_controller import ExitController
from data_models.receipt import Receipt
from sensors.light_sensor import LightSensor
from controller.light_controller import LightController

import threading
def main():
    

    print("Smart Parking System Started...\n")
    ultrasonic = UltrasonicSensor()
    camera = CameraSensor()
    model = VehicleClassificationModel()
    slot = ParkingSlot()
    ticket = Ticket()


    entry_controller = EntryController(
        ultrasonic, camera, model, slot, ticket
    )

    receipt = Receipt("", 0)

    exit_controller = ExitController(
        ultrasonic, slot, ticket, receipt
    )
    # light_sensor = LightSensor()
    # light_controller = LightController(light_sensor)

    # # Run light system in a separate thread
    # light_thread = threading.Thread(target=light_controller.run, daemon=True)
    # light_thread.start()
    print(" Smart Parking System Started...\n")

    while True:
        entry_controller.process_vehicle()
        print(" Waiting 5 seconds...\n")
        time.sleep(5)
        exit_controller.process_exit()
        print(" Waiting 5 seconds...\n")
        time.sleep(5)


if __name__ == "__main__":
    main()