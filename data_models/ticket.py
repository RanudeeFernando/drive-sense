import csv
from datetime import datetime
import os
from data_models.parking_slot import ParkingSlot

class Ticket:
    def __init__(self, ticket_id: str = "DST-1", parking_slot: ParkingSlot = 1, vehicle_type: str = "car", entry_time: str = "2026-03-31 00:42:03"):
        self._ticket_id = ticket_id
        self._parking_slot = parking_slot
        self._vehicle_type = vehicle_type
        self._entry_time = entry_time
        

    def get_ticket_id(self) -> str:
        return self._ticket_id

    def set_ticket_id(self, ticket_id: str) -> None:
        self._ticket_id = ticket_id

    def get_parking_slot(self) -> ParkingSlot:
        return self._parking_slot

    def set_parking_slot(self, parking_slot: ParkingSlot) -> None:
        self._parking_slot = parking_slot

    def get_vehicle_type(self) -> str:
        return self._vehicle_type

    def set_vehicle_type(self, vehicle_type: str) -> None:
        self._vehicle_type = vehicle_type

    def get_entry_time(self) -> str:
        return self._entry_time

    def set_entry_time(self, entry_time: str) -> None:
        self._entry_time = entry_time

    def generate_ticket(self, slot_id, vehicle_type) -> str:
        tickets_file = "data/tickets.csv"
        last_number = 0
        tickets = []

        # Read existing tickets if file exists
        if os.path.exists(tickets_file):
            with open(tickets_file, "r", newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    tickets.append(row)
                    try:
                        num = int(row["ticket_id"].split("-")[1])
                        if num > last_number:
                            last_number = num
                    except:
                        continue

        # Generate new ticket ID
        new_ticket_id = f"DST-{last_number + 1}"

        # Create new ticket row with entry_time
        new_ticket = {
            "ticket_id": new_ticket_id,
            "slot_id": slot_id,
            "vehicle_type": vehicle_type,
            "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tickets.append(new_ticket)

        # Determine fieldnames dynamically to include all columns
        fieldnames = tickets[0].keys() if tickets else ["ticket_id", "slot_id", "vehicle_type", "entry_time"]

        # Write updated tickets back to CSV
        with open(tickets_file, "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tickets)

        print(f"🎟️ Ticket {new_ticket_id} generated for slot {slot_id}")
        return new_ticket_id