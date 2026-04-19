from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import threading
import time as _time
from typing import Optional

from raspberry_pi.repositories.slot_repository import SlotRepository
from raspberry_pi.repositories.ticket_repository import TicketRepository
from raspberry_pi.sensors.led_light import LEDLight
from raspberry_pi.services.slot_manager_service import SlotManagerService
from raspberry_pi.services.ticket_manager_service import TicketManagerService

router = APIRouter()

_driver_status: dict = {
    "status": "idle",
    "message": "",
    "ticket": None,
}
_status_lock = threading.Lock()
_reset_timer: Optional[threading.Timer] = None

SUCCESS_RESET_DELAY = 20  # driver needs time to read slot + PIN
ERROR_RESET_DELAY = 12   # enough to read the error message


def _schedule_reset(delay: int):
    """Cancel any pending reset timer and start a fresh one."""
    global _reset_timer
    if _reset_timer is not None:
        _reset_timer.cancel()

    def _do_reset():
        with _status_lock:
            _driver_status["status"] = "idle"
            _driver_status["message"] = ""
            _driver_status["ticket"] = None

    _reset_timer = threading.Timer(delay, _do_reset)
    _reset_timer.daemon = True
    _reset_timer.start()

# Repositories
slot_repository = SlotRepository()
ticket_repository = TicketRepository()
green_light=LEDLight(pin=17)
red_light=LEDLight(pin=27)

# Services
slot_manager_service = SlotManagerService(slot_repository)
ticket_manager_service = TicketManagerService(
    ticket_repository=ticket_repository,
    slot_manager_service=slot_manager_service,
    green_light=green_light,
    red_light=red_light
)


class VerifyPinRequest(BaseModel):
    pin_code: str

class DriverStatusUpdate(BaseModel):
    status: str           # "processing" | "success" | "error"
    message: str = ""
    ticket: Optional[dict] = None


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

@router.get("/driver-view/status")
def get_driver_status():
    """Polled by the entry dashboard every 2 s to drive the UI state machine."""
    with _status_lock:
        # Also expose the reset delays so the UI can sync its countdown
        return {
            **_driver_status,
            "success_reset_delay": SUCCESS_RESET_DELAY,
            "error_reset_delay": ERROR_RESET_DELAY,
        }


@router.put("/driver-view/status")
def update_driver_status(req: DriverStatusUpdate):
    """Called by the Raspberry Pi to push state transitions."""
    global _reset_timer

    allowed = {"processing", "success", "error"}
    if req.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{req.status}'. Must be one of: {allowed}"
        )

    with _status_lock:
        _driver_status["status"] = req.status
        _driver_status["message"] = req.message
        _driver_status["ticket"] = req.ticket

    # Auto-reset to idle after success or error so the welcome screen restores
    if req.status == "success":
        _schedule_reset(SUCCESS_RESET_DELAY)
    elif req.status == "error":
        _schedule_reset(ERROR_RESET_DELAY)
    else:
        # Cancel any lingering reset timer when processing starts fresh
        if _reset_timer is not None:
            _reset_timer.cancel()
            _reset_timer = None

    return {"ok": True, "status": req.status}