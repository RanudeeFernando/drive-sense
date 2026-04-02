from datetime import datetime


class TicketManager:
    def __init__(self):
        self.active_tickets = {}

    def create_entry_ticket(self, ticket):
        self.active_tickets[ticket.slot_id] = ticket
        return ticket

    def close_ticket(self, slot_id):
        ticket = self.active_tickets.get(slot_id)

        if ticket is None:
            return None

        ticket.exit_time = datetime.now()
        duration = ticket.exit_time - ticket.entry_time
        ticket.total_minutes = int(duration.total_seconds() // 60)
        ticket.price = self.calculate_price(ticket.vehicle_type, ticket.total_minutes)

        del self.active_tickets[slot_id]
        return ticket

    def calculate_price(self, vehicle_type, duration_minutes):
        rates = {
            "bike": 50,
            "car": 100,
            "lorry": 150,
        }

        hours = max(1, duration_minutes / 60)
        return round(rates.get(vehicle_type, 100) * hours, 2)