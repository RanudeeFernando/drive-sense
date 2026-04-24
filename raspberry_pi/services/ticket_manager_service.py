from datetime import datetime
import threading
import time

from raspberry_pi.data_models.vehicle_type import VehicleType, PARKING_RATES


class TicketManagerService:
    def __init__(self, ticket_repository, slot_manager_service, green_light,red_light):
        self.ticket_repository = ticket_repository
        self.slot_manager_service = slot_manager_service
        self.green_light = green_light
        self.red_light = red_light
    
    def _allow_exit_signal(self):
        self.red_light.turn_off()
        self.green_light.turn_on()
        
        time.sleep(10)

        self.green_light.turn_off()
        self.red_light.turn_on()

        

    def allocate_ticket(self, vehicle_type: VehicleType) -> dict:
        available_slot = self.slot_manager_service.find_available_slot(vehicle_type)

        if not available_slot:
            return {
                "status": "failed",
                "message": f"No available slot for vehicle type: {vehicle_type.value}"
            }

        reserved = self.slot_manager_service.reserve_slot(available_slot.get_slot_id())
        if not reserved:
            return {
                "status": "failed",
                "message": f"Failed to reserve slot: {available_slot.get_slot_id()}"
            }

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


    def process_exit_by_pin(self, pin_code: str) -> dict:
        ticket = self.ticket_repository.get_active_ticket_by_pin(pin_code)

        if ticket is None:
            return {
                "status": "failed",
                "message": f"No active ticket found with PIN: {pin_code}"
            }
        
        slot_id = ticket.get_slot_id()
        
        # Check if there are more than 1 active tickets for this slot
        # If so, don't release the slot (another vehicle has parked in the meantime)
        active_ticket_count = self.ticket_repository.count_active_tickets_by_slot_id(slot_id)
        
        if active_ticket_count > 1:
            return {
                "status": "failed",
                "message": f"Cannot release slot {slot_id}. Another vehicle is currently parked in this slot."
            }
        
        # Only release if there's exactly 1 active ticket (the current one)
        self.slot_manager_service.release_slot_by_id(slot_id)

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
            "duration_hours": round(duration_hours, 2),
            "price": price,
            "message": "Exit processed successfully"
        }

    def process_payment(self, ticket_id: str) -> dict:
        ticket = self.ticket_repository.get_ticket_by_id(ticket_id)
        if ticket is None:
            return {
                "status": "failed",
                "message": f"Ticket not found: {ticket_id}"
            }
        
        threading.Thread(target=self._allow_exit_signal, daemon=True).start()
        
        return {
            "status": "success",
            "message": "Payment verified, gate opened."
        }