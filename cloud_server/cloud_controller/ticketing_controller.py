# cloud_server/cloud_controller/ticketing_controller.py
from cloud_server.data_models.parking_slot import ParkingSlot
from cloud_server.data_models.ticket import Ticket

class TicketingController:
    def __init__(self, slot, ticket):
        self.slot = slot
        self.ticket = ticket

    def allocate_ticket(self, vehicle_type: str):
        # find available slot
        slot_id = self.slot.find_available_slot(vehicle_type)

        if slot_id:
            # reserve slot
            self.slot.reserve_slot(slot_id)

            #  generate ticket
            ticket_id = self.ticket.generate_ticket(slot_id, vehicle_type)

            print(f" Slot {slot_id} allocated for {vehicle_type}. Ticket: {ticket_id}")
            return {"status": "success", "ticket_id": ticket_id, "slot_id": slot_id}
        else:
            print(f" No slots available for {vehicle_type}!")
            return {"status": "failed", "message": "No slots available"}
