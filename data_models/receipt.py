import csv
from datetime import datetime
import os

class Receipt:
    def __init__(self, exit_time: str = "", price: float = 0.0):
        self._exit_time = exit_time
        self._price = price

    def get_exit_time(self) -> str:
        return self._exit_time

    def set_exit_time(self, exit_time: str) -> None:
        self._exit_time = exit_time

    def get_price(self) -> float:
        return self._price

    def set_price(self, price: float) -> None:
        self._price = price

    def generate_receipt(self, ticket_id: str, slot_id: int, vehicle_type: str) -> str:
        # Save receipt to CSV
        receipts_file = "data/receipts.csv"
        receipt_row = {
            "ticket_id": ticket_id,
            "slot_id": slot_id,
            "vehicle_type": vehicle_type,
            "exit_time": self._exit_time,
            "total_amount": f"{self._price:.2f}"
        }

        # Read existing receipts
        rows = []
        if os.path.exists(receipts_file):
            with open(receipts_file, "r", newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

        # Add new receipt
        rows.append(receipt_row)

        # Write updated CSV
        with open(receipts_file, "w", newline="") as file:
            fieldnames = ["ticket_id", "slot_id", "vehicle_type", "exit_time", "total_amount"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        # Return printable receipt
        return (f"--- RECEIPT ---\n"
                f"Ticket ID: {ticket_id}\n"
                f"Slot ID: {slot_id}\n"
                f"Vehicle Type: {vehicle_type}\n"
                f"Exit Time: {self._exit_time}\n"
                f"Total Amount: Rs.{self._price:.2f}\n"
                f"---------------")

    def calculate_price(self, vehicle_type: str, duration_hours: float) -> float:
        rates = {'bike': 50, 'car': 100, 'lorry': 130}
        rate = rates.get(vehicle_type.lower(), 100)
        self._price = rate * duration_hours
        return self._price