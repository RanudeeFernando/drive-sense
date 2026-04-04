from fastapi import APIRouter
from pydantic import BaseModel

from cloud_server.cloud_controller.ticketing_controller import TicketingController
from cloud_server.cloud_controller.slot_release_controller import SlotReleaseController
from cloud_server.cloud_controller.receipt_controller import ReceiptController
from cloud_server.cloud_controller.light_controller import LightController

router = APIRouter()


# Controller instances

ticketing_controller = TicketingController()
slot_release_controller = SlotReleaseController()
receipt_controller = ReceiptController()
light_controller = LightController()


# Request models

class TicketingRequest(BaseModel):
    vehicle_type: str


class SlotReleaseRequest(BaseModel):
    distance: float


class ReceiptRequest(BaseModel):
    ticket_id: str


class LightRequest(BaseModel):
    resistance: float


class ManualLightRequest(BaseModel):
    light_on: bool


class ThresholdRequest(BaseModel):
    threshold: float



# Ticketing endpoints

@router.post("/ticketing")
def create_ticket(request: TicketingRequest):
    return ticketing_controller.process_ticket(request.vehicle_type)



# Slot release endpoints

@router.post("/release_slot")
def release_slot(request: SlotReleaseRequest):
    return slot_release_controller.process_slot_release(request.distance)



# Receipt / billing endpoints

@router.post("/ereceipt")
def generate_receipt(request: ReceiptRequest):
    return receipt_controller.process_receipt(request.ticket_id)



# Light control endpoints

@router.post("/light")
def process_light(request: LightRequest):
    return light_controller.process_light(request.resistance)


@router.post("/light/manual")
def set_manual_light(request: ManualLightRequest):
    return light_controller.set_manual_mode(request.light_on)


@router.post("/light/auto")
def set_auto_light():
    return light_controller.set_auto_mode()


@router.post("/light/threshold")
def update_light_threshold(request: ThresholdRequest):
    return light_controller.update_threshold(request.threshold)


@router.get("/light/status")
def get_light_status():
    return light_controller.get_light_status()