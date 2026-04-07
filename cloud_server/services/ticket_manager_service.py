
from datetime import datetime

from cloud_server.data_models.vehicle_type import VehicleType, PARKING_RATES


class TicketManagerService:
    def __init__(self, ticket_repository, slot_manager_service):
        self.ticket_repository = ticket_repository
        self.slot_manager_service = slot_manager_service

    def allocate_ticket(self, vehicle_type: VehicleType) -> dict:
        available_slot = self.slot_manager_service.find_available_slot(vehicle_type)

        if not available_slot:
            return {
                "status": "failed",
                "message": f"No available slot for vehicle type: {vehicle_type.value}"
            }

        self.slot_manager_service.reserve_slot(available_slot.get_slot_id())

        ticket_data = self.ticket_repository.generate_ticket(
            parking_slot=available_slot,
            vehicle_type=vehicle_type
        )

        return {
            "status": "success",
            "ticket_id": ticket_data["ticket_id"],
            "slot_id": available_slot.get_slot_id(),
            "slot_type": available_slot.get_slot_type().value,
            "vehicle_type": ticket_data["vehicle_type"],
            "entry_time": ticket_data["entry_time"],
            "pin_code": ticket_data["pin_code"]
        }

    def generate_e_receipt(self, ticket_id: str) -> dict:
        ticket = self.ticket_repository.get_ticket_by_id(ticket_id)

        if ticket is None:
            return {
                "status": "failed",
                "message": f"Ticket not found: {ticket_id}"
            }

        if ticket.get_status() == "closed":
            return {
                "status": "failed",
                "message": f"Ticket already closed: {ticket_id}"
            }

        slot_id = ticket.get_slot_id()

        active_ticket = self.ticket_repository.get_active_ticket_by_slot_id(slot_id)
        if active_ticket is None:
            return {
                "status": "failed",
                "message": f"No active ticket found for slot: {slot_id}"
            }

        self.slot_manager_service.release_slot(slot_id)

        entry_time = datetime.strptime(ticket.get_entry_time(), "%Y-%m-%d %H:%M:%S")
        exit_time = datetime.now()

        duration_minutes = (exit_time - entry_time).total_seconds() / 60.0
        duration_hours = duration_minutes / 60.0

        rate_per_hour = PARKING_RATES[ticket.get_vehicle_type()]
        price = round(duration_hours * rate_per_hour, 2)

        self.ticket_repository.update_ticket_on_exit(
            ticket_id=ticket.get_ticket_id(),
            exit_time=exit_time,
            duration_minutes=duration_minutes,
            price=price
        )

        return {
            "status": "success",
            "ticket_id": ticket.get_ticket_id(),
            "slot_id": slot_id,
            "vehicle_type": ticket.get_vehicle_type().value,
            "entry_time": ticket.get_entry_time(),
            "exit_time": exit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": round(duration_minutes, 2),
            "price": price,
            "message": "E-receipt generated successfully"
        }