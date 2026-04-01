# api_app.py
from fastapi import FastAPI
from pydantic import BaseModel
import threading
import time

# Import your parking system modules
from sensors.ultrasonic_sensor import UltrasonicSensor
from sensors.camera_sensor import CameraSensor
from ml_models.vehicle_classification_model import VehicleClassificationModel
from data_models.parking_slot import ParkingSlot
from data_models.ticket import Ticket
from controller.entry_controller import EntryController
from controller.exit_controller import ExitController
from data_models.receipt import Receipt

app = FastAPI(title="Smart Parking System API")

# Initialize the system once at startup
ultrasonic = UltrasonicSensor()
camera = CameraSensor()
model = VehicleClassificationModel()
slot = ParkingSlot()
ticket = Ticket()
receipt = Receipt("", 0)

entry_controller = EntryController(ultrasonic, camera, model, slot, ticket)
exit_controller = ExitController(ultrasonic, slot, ticket, receipt)

# Optional: Background thread for lights if needed
# from sensors.light_sensor import LightSensor
# from controller.light_controller import LightController
# light_sensor = LightSensor()
# light_controller = LightController(light_sensor)
# threading.Thread(target=light_controller.run, daemon=True).start()

@app.get("/")
def health_check():
    return {"message": "Smart Parking System API is running!"}

@app.post("/process-entry")
def process_entry():
    try:
        vehicle_info = entry_controller.process_vehicle()
        return {"status": "success", "vehicle_info": vehicle_info}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/process-exit")
def process_exit():
    try:
        exit_info = exit_controller.process_exit()
        return {"status": "success", "exit_info": exit_info}
    except Exception as e:
        return {"status": "error", "detail": str(e)}