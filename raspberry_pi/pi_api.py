from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from raspberry_pi.repositories.slot_repository import SlotRepository
from raspberry_pi.repositories.ticket_repository import TicketRepository
from raspberry_pi.services.slot_manager_service import SlotManagerService
from raspberry_pi.services.ticket_manager_service import TicketManagerService

router = APIRouter()

# Repositories
slot_repository = SlotRepository()
ticket_repository = TicketRepository()

# Services
slot_manager_service = SlotManagerService(slot_repository)
ticket_manager_service = TicketManagerService(
    ticket_repository=ticket_repository,
    slot_manager_service=slot_manager_service
)


class VerifyPinRequest(BaseModel):
    pin_code: str


@router.get("/")
def home():
    return {"message": "Smart Parking Raspberry Pi API Running!"}


@router.get("/driver-view/latest")
def get_latest_driver_view():
    tickets = ticket_repository.get_all_tickets()

    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found")

    latest_ticket = tickets[0]

    return {
        "system_name": "Drive Sense AI",
        "welcome_message": "Welcome to the Smart Vehicle Parking System",
        "ticket_id": latest_ticket.get_ticket_id(),
        "slot_id": latest_ticket.get_slot_id(),
        "vehicle_type": latest_ticket.get_vehicle_type().value,
        "entry_time": latest_ticket.get_entry_time(),
        "pin_code": latest_ticket.get_pin_code()
    }


@router.post("/exit/verify-pin")
def process_exit_by_pin(req: VerifyPinRequest):
    result = ticket_manager_service.process_exit_by_pin(req.pin_code)

    if result["status"] == "failed":
        raise HTTPException(status_code=400, detail=result["message"])

    return result