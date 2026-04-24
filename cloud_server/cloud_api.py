from fastapi import APIRouter, HTTPException, UploadFile, File
import shutil
from pydantic import BaseModel


from cloud_server.services.light_manager_service import LightManagerService

from cloud_server.repositories.slot_repository import SlotRepository
from cloud_server.repositories.ticket_repository import TicketRepository
from cloud_server.repositories.light_repository import LightRepository
from cloud_server.services.admin_service import AdminService

import os
from datetime import datetime   


router = APIRouter()


slot_repository = SlotRepository()
ticket_repository = TicketRepository()



light_manager_service = LightManagerService()


admin_service = AdminService(light_manager_service=light_manager_service)


class AdminLoginRequest(BaseModel):
    username: str
    password: str

class LightRequest(BaseModel):
    light_on: bool


class LDRControlRequest(BaseModel):
    enabled: bool

@router.post("/lighting")
def control_light(req: LightRequest):
    """Endpoint to receive light status updates from the Raspberry Pi"""
    return light_manager_service.process_light(req.light_on)


@router.post("/login")
def admin_login(req: AdminLoginRequest):
    """Endpoint for admin login. Validates credentials and returns success or failure"""
    result = admin_service.login(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@router.get("/slots_availability")
def get_slot_availability():
    """Endpoint to get the current availability status of all parking slots"""
    slots = slot_repository.get_all_slots()
    return [
        {"slot_id": slot.get_slot_id(), "is_occupied": slot.get_slot_status()}
        for slot in slots
    ]


@router.get("/parking_logs")
def get_parking_logs():
    """Endpoint to get all parking tickets/logs, ordered by entry time descending"""
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
    """Endpoint to control the LDR status"""
    return admin_service.set_ldr_status(req.enabled)


@router.get("/ldr-status")
def get_ldr_status():
    """Endpoint to get the current LDR status"""
    return {"enabled": admin_service.get_ldr_status()}


@router.get("/light-logs")
def get_light_logs():
    """Endpoint to retrieve all light on/off logs"""
    repo = LightRepository()
    return repo.get_all_logs()



DATA_DIR = "cloud_server/model_train/Data"
CLASSES = ["car", "bike", "lorry", "unknown"]

for cls in CLASSES:
    os.makedirs(os.path.join(DATA_DIR, cls), exist_ok=True)

@router.post("/upload-image/{vehicle_type}")
async def upload_image(vehicle_type: str, file: UploadFile = File(...)):
    """Endpoint to upload an image for a specific vehicle type. Saves the file in the corresponding class folder with a timestamped filename."""
    if vehicle_type.lower() not in CLASSES:
        return {"status": "error", "message": f"Invalid vehicle type: {vehicle_type}"}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{vehicle_type}_{timestamp}.jpg"
    save_path = os.path.join(DATA_DIR, vehicle_type.lower(), filename)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"status": "success", "filename": filename, "path": save_path}