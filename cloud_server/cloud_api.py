from fastapi import APIRouter
from pydantic import BaseModel

from cloud_server.services.slot_manager_service import SlotManagerService
from cloud_server.services.ticket_manager_service import TicketManagerService
from cloud_server.services.light_controller import LightController

from cloud_server.repositories.slot_repository import SlotRepository
from cloud_server.repositories.ticket_repository import TicketRepository

from cloud_server.data_models.vehicle_type import VehicleType

router = APIRouter()

# Initialize repositories
slot_repository = SlotRepository()
ticket_repository = TicketRepository()

# Initialize services
slot_manager_service = SlotManagerService(slot_repository)
ticket_manager_service = TicketManagerService(
    ticket_repository=ticket_repository,
    slot_manager_service=slot_manager_service
)

# Keep light separately for now
light_controller = LightController()


# Pydantic schemas for request bodies
class TicketingRequest(BaseModel):
    vehicle_type: VehicleType


class SlotReleaseRequest(BaseModel):
    distance: float


class ReceiptRequest(BaseModel):
    ticket_id: str


class LightRequest(BaseModel):
    resistance: float


@router.post("/ticket")
def allocate_ticket(req: TicketingRequest):
    return ticket_manager_service.allocate_ticket(req.vehicle_type)


@router.post("/release-slot")
def process_slot_release(req: SlotReleaseRequest):
    return slot_manager_service.release_slot_by_distance(req.distance)


@router.post("/ticket-receipt")
def get_receipt(req: ReceiptRequest):
    return ticket_manager_service.generate_e_receipt(req.ticket_id)


@router.post("/lighting")
def control_light(req: LightRequest):
    return light_controller.process_light(req.resistance)