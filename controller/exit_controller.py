# controller/exit_controller.py

from datetime import datetime
import csv

class ExitController:

    def __init__(self, ultrasonic, slot, ticket, receipt):
        self.ultrasonic = ultrasonic
        self.slot = slot
        self.ticket = ticket
        self.receipt = receipt

    def get_ticket_by_id(self, ticket_id: str):
        """Return ticket row from tickets.csv by ticket_id, only if exit_time is empty"""
        with open("data/tickets.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["ticket_id"] == ticket_id and row.get("exit_time", "") == "":
                    return row
        return None
    def process_exit(self):
    # Step 0: Ask driver for ticket ID
        ticket_id = input("🎫 Please enter your ticket ID: ").strip()

        # Step 1: fetch ticket data from CSV
        ticket_data = self.get_ticket_by_id(ticket_id)
        if not ticket_data:
            print("❌ Ticket not found or already exited!")
            return

        slot_id = int(ticket_data["slot_id"])
        vehicle_type = ticket_data["vehicle_type"]
        print(f"📍 Vehicle exiting from Slot {slot_id} (Vehicle: {vehicle_type})")

        # Step 2: release slot
        self.slot.release_slot(slot_id)

        # Step 3: calculate duration
        entry_time = datetime.strptime(ticket_data["entry_time"], "%Y-%m-%d %H:%M:%S")
        exit_time = datetime.now()

        duration_minutes = (exit_time - entry_time).total_seconds() / 60
        duration_hours = duration_minutes / 60

        # Step 4: calculate price
        price = self.receipt.calculate_price(vehicle_type, duration_hours)

        # Step 5: generate receipt and update CSV
        self.receipt.set_exit_time(exit_time.strftime("%Y-%m-%d %H:%M:%S"))
        receipt_text = self.receipt.generate_receipt(ticket_id, slot_id, vehicle_type)
        print(receipt_text)

        # Step 6: update ticket CSV with exit time
        self.update_ticket_exit(ticket_id)

    # -----------------------------
    # Helper: find ticket by slot
    # -----------------------------
    def get_ticket_by_slot(self, slot_id):
        with open("data/tickets.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["slot_id"] == str(slot_id) and row.get("exit_time", "") == "":
                    return row
        return None

    # -----------------------------
    # Helper: update exit time
    # -----------------------------
    def update_ticket_exit(self, ticket_id):
        rows = []

        with open("data/tickets.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["ticket_id"] == ticket_id:
                    row["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rows.append(row)

        with open("data/tickets.csv", "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)