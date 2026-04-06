from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cloud_server.services.slot_manager_service import SlotManagerService
from cloud_server.services.ticket_manager_service import TicketManagerService
from cloud_server.services.light_controller import LightController

from cloud_server.repositories.slot_repository import SlotRepository
from cloud_server.repositories.ticket_repository import TicketRepository

from cloud_server.services.admin_service import AdminService
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

# Initialize admin service
admin_service = AdminService(light_controller=light_controller)


# Pydantic schemas for request bodies
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class TicketingRequest(BaseModel):
    vehicle_type: VehicleType


class SlotReleaseRequest(BaseModel):
    distance: float


class ReceiptRequest(BaseModel):
    ticket_id: str


class LightRequest(BaseModel):
    light_on: bool


class LDRControlRequest(BaseModel):
    enabled: bool


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
    return light_controller.process_light(req.light_on)


@router.post("/login")
def admin_login(req: AdminLoginRequest):
    result = admin_service.login(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@router.get("/slots_availability")
def get_slot_availability():
    slots = slot_repository.get_all_slots()
    return [
        {"slot_id": slot.get_slot_id(), "is_occupied": slot.get_slot_status()}
        for slot in slots
    ]


@router.get("/parking_logs")
def get_parking_logs():
    tickets = ticket_repository.get_all_tickets()
    return [
        {
            "ticket_id": ticket.get_ticket_id(),
            "vehicle_type": ticket.get_vehicle_type().value,
            "slot_id": ticket.get_slot_id(),
            "entry_time": ticket.get_entry_time(),
            "exit_time": ticket.get_exit_time(),
            "status": ticket.get_status(),
            "price": ticket.get_price(),
        }
        for ticket in tickets
    ]


@router.post("/ldr-control")
def set_ldr_control(req: LDRControlRequest):
    return admin_service.set_ldr_status(req.enabled)


@router.get("/ldr-status")
def get_ldr_status():
    return {"enabled": admin_service.get_ldr_status()}
