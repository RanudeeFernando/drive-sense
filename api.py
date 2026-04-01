# api.py

from fastapi import APIRouter

from sensors.ultrasonic_sensor import UltrasonicSensor
from sensors.camera_sensor import CameraSensor
from ml_models.vehicle_classification_model import VehicleClassificationModel
from data_models.parking_slot import ParkingSlot
from data_models.ticket import Ticket
from controller.entry_controller import EntryController
from controller.exit_controller import ExitController
from data_models.receipt import Receipt
from sensors.light_sensor import LightSensor
from controller.light_controller import LightController

# Create router
router = APIRouter()

# Initialize shared system (IMPORTANT: only once)
ultrasonic = UltrasonicSensor()
camera = CameraSensor()
model = VehicleClassificationModel()
slot = ParkingSlot()
ticket = Ticket()
receipt = Receipt("", 0)
light_sensor = LightSensor()

entry_controller = EntryController(
    ultrasonic, camera, model, slot, ticket
)

exit_controller = ExitController(
    ultrasonic, slot, ticket, receipt
)

light_controller = LightController(light_sensor)

@router.post("/entry")
def vehicle_entry():
    entry_controller.process_vehicle()
    return {"message": "Vehicle entry processed"}


@router.post("/exit")
def vehicle_exit():
    exit_controller.process_exit()
    return {"message": "Vehicle exit processed"}


@router.post("/light")
def control_light():
    light_controller.run()
    return {"message": "Light system triggered"}