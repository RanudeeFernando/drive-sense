# cloud_server/services/ticket_manager_service.py
from datetime import datetime
from cloud_server.data_models.vehicle_type import VehicleType, PARKING_RATES

class TicketManagerService:
    def __init__(self, ticket_repository, slot_manager_service):
        self.ticket_repository = ticket_repository
        self.slot_manager_service = slot_manager_service

    def allocate_ticket(self, vehicle_type: VehicleType):
        slot = self.slot_manager_service.find_available_slot(vehicle_type)

        if slot is None:
            print(f"No slots available for {vehicle_type.value}!")
            return {
                "status": "failed",
                "message": "No slots available"
            }

        reserved = self.slot_manager_service.reserve_slot(slot.get_slot_id())
        if not reserved:
            return {
                "status": "failed",
                "message": "Slot reservation failed"
            }

        ticket_id = self.ticket_repository.generate_ticket(
            slot,
            vehicle_type
        )

        print(
            f"Slot {slot.get_slot_id()} allocated for "
            f"{slot.get_slot_type().value}. Ticket: {ticket_id}"
        )

        return {
            "status": "success",
            "ticket_id": ticket_id,
            "slot_id": slot.get_slot_id(),
            "slot_type": slot.get_slot_type().value
        }

    def generate_e_receipt(self, ticket_id: str):
        ticket = self.ticket_repository.get_ticket_by_id(ticket_id)

        if not ticket:
            print("Ticket not found!")
            return {
                "status": "failed",
                "message": "Ticket not found"
            }

        if ticket.get_status() == "closed":
            return {
                "status": "failed",
                "message": "Ticket already closed"
            }

        slot = ticket.get_parking_slot()
        slot_id = slot.get_slot_id()
        vehicle_type = ticket.get_vehicle_type()
        entry_time = ticket.get_entry_time()

        if not self.slot_manager_service.is_slot_released(slot_id):
            print(f"Slot {slot_id} is still occupied! Releasing now...")
            self.slot_manager_service.release_slot_by_id(slot_id)

        try:
            entry_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
        except Exception:
            entry_dt = datetime.now()

        exit_time = datetime.now()
        duration_minutes = (exit_time - entry_dt).total_seconds() / 60
        duration_hours = max(duration_minutes / 60, 0.01)

        hourly_rate = PARKING_RATES[vehicle_type]
        price = round(hourly_rate * duration_hours, 2)

        updated = self.ticket_repository.update_ticket_on_exit(
            ticket_id=ticket_id,
            exit_time=exit_time,
            duration_minutes=duration_minutes,
            price=price
        )

        if not updated:
            return {
                "status": "failed",
                "message": "Could not update ticket on exit"
            }

        receipt_text = (
            f"Ticket ID: {ticket.get_ticket_id()}\n"
            f"Slot ID: {slot_id}\n"
            f"Vehicle Type: {vehicle_type.value}\n"
            f"Entry Time: {entry_time}\n"
            f"Exit Time: {exit_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Duration (minutes): {round(duration_minutes, 2)}\n"
            f"Price: Rs. {price}"
        )

        print(receipt_text)

        return {
            "status": "success",
            "ticket_id": ticket.get_ticket_id(),
            "slot_id": slot_id,
            "vehicle_type": vehicle_type.value,
            "entry_time": entry_time,
            "exit_time": exit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": round(duration_minutes, 2),
            "price": price
        }