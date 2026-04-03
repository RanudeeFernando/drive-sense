# cloud_server/cloud_controller/receipt_controller.py
from datetime import datetime
import csv

class ReceiptController:
    def __init__(self, receipt, slot):
        self.receipt = receipt
        self.slot = slot

    def get_ticket_by_id(self, ticket_id: str):
        with open("cloud_server/data/tickets.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["ticket_id"] == ticket_id and row.get("exit_time", "") == "":
                    return row
        return None

    def is_slot_released(self, slot_id: int):
        with open("cloud_server/data/slots.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["slot_id"] == str(slot_id):
                    return row["is_occupied"] == "False"
        return False

    def generate_ereceipt(self, ticket_id: str):
        # fetch ticket data from CSV
        ticket_data = self.get_ticket_by_id(ticket_id)
        if not ticket_data:
            print("❌ Ticket not found or already exited!")
            return {"status": "failed", "message": "Ticket not found or already exited"}

        slot_id = int(ticket_data["slot_id"])
        vehicle_type = ticket_data["vehicle_type"]
        entry_time = ticket_data["entry_time"]

        # verifyslot is successfully released first
        if not self.is_slot_released(slot_id):
            print(f"❌ Slot {slot_id} is still occupied! now releasing")
            self.slot.release_slot(slot_id)

        # calculate duration
        try:
            entry_time = datetime.strptime(ticket_data["entry_time"], "%Y-%m-%d %H:%M:%S")
        except:
            entry_time = datetime.now()
            
        exit_time = datetime.now()
        duration_minutes = (exit_time - entry_time).total_seconds() / 60
        duration_hours = max(duration_minutes / 60, 0.01)

        # calculate price
        price = self.receipt.calculate_price(vehicle_type, duration_hours)

        # generate receipt and update CSV
        self.receipt.set_exit_time(exit_time.strftime("%Y-%m-%d %H:%M:%S"))
        receipt_text = self.receipt.generate_receipt(ticket_id, slot_id, vehicle_type, entry_time)
        
        #  update ticket CSV with exit time
        self.update_ticket_exit(ticket_id)
        
        print(receipt_text)
        return {
            "status": "success",
            "receipt": receipt_text,
            "price": price,
            "duration_minutes": duration_minutes
        }

    def update_ticket_exit(self, ticket_id):
        rows = []
        with open("cloud_server/data/tickets.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["ticket_id"] == ticket_id:
                    row["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rows.append(row)

        with open("cloud_server/data/tickets.csv", "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
