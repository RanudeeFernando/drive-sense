from fastapi import APIRouter
from pydantic import BaseModel
from cloud_server.cloud_controller.ticketing_controller import TicketingController
from cloud_server.cloud_controller.slot_release_controller import SlotReleaseController
from cloud_server.cloud_controller.receipt_controller import ReceiptController
from cloud_server.cloud_controller.light_controller import LightController
from cloud_server.data_models.parking_slot import ParkingSlot
from cloud_server.data_models.ticket import Ticket
from cloud_server.data_models.receipt import Receipt

router = APIRouter()

# Initialize classes
slot = ParkingSlot()
ticket = Ticket()
receipt = Receipt("", 0)

# Initialize controllers
ticketing_controller = TicketingController(slot, ticket)
slot_release_controller = SlotReleaseController(slot)
receipt_controller = ReceiptController(receipt, slot)
light_controller = LightController()

# Pydantic schemas for request bodies
class TicketingRequest(BaseModel):
    vehicle_type: str

class SlotReleaseRequest(BaseModel):
    distance: float

class ReceiptRequest(BaseModel):
    ticket_id: str

class LightRequest(BaseModel):
    resistance: float


@router.post("/ticketing")
def allocate_ticket(req: TicketingRequest):
    return ticketing_controller.allocate_ticket(req.vehicle_type)


@router.post("/release_slot")
def process_slot_release(req: SlotReleaseRequest):
    return slot_release_controller.process_slot_release(req.distance)


@router.post("/ereceipt")
def get_receipt(req: ReceiptRequest):
    return receipt_controller.generate_ereceipt(req.ticket_id)


@router.post("/light")
def control_light(req: LightRequest):
    return light_controller.process_light(req.resistance)
