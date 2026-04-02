from datetime import datetime
from data_models.ticket import Ticket
from core.slot_allocator import SlotAllocator
from core.ticket_manager import TicketManager
from data_models.receipt import Receipt


class ParkingManager:
    def __init__(self, slots):
        self.slots = slots
        self.slot_allocator = SlotAllocator(slots)
        self.ticket_manager = TicketManager()
        self.ticket_counter = 1

    def vehicle_entry(self, vehicle_type):
        slot = self.slot_allocator.allocate_slot(vehicle_type)

        if slot is None:
            return None

        slot.allocate_slot()

        ticket = Ticket(
            ticket_id=self.ticket_counter,
            slot_id=slot.slot_id,
            vehicle_type=vehicle_type,
            entry_time=datetime.now(),
        )

        self.ticket_counter += 1
        self.ticket_manager.create_entry_ticket(ticket)
        return ticket

    def vehicle_exit(self, slot_id):
        for slot in self.slots:
            if slot.slot_id == slot_id:
                slot.release_slot()
                break

        ticket = self.ticket_manager.close_ticket(slot_id)
        return ticket

    def generate_receipt(self, ticket):
        if ticket is None:
            return None

        receipt = Receipt(exit_time=str(ticket.exit_time))
        receipt.calculate_price(ticket.total_minutes, ticket.vehicle_type)
        return receipt