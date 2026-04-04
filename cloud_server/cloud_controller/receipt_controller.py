# cloud_server/cloud_controller/receipt_controller.py
from datetime import datetime
from cloud_server.cloud.firestore_client import get_db


class ReceiptController:
    def __init__(self, receipt, slot):
        self.receipt = receipt
        self.slot = slot

    def get_ticket_by_id(self, ticket_id: str):
        """Fetch an open ticket (no exit_time yet) from Firestore."""
        db = get_db()
        doc = db.collection("tickets").document(ticket_id).get()
        if doc.exists:
            data = doc.to_dict()
            if data.get("exit_time", "") == "":
                return data
        return None

    def is_slot_released(self, slot_id: int) -> bool:
        """Check whether a slot is marked as free in Firestore."""
        db = get_db()
        doc = db.collection("slots").document(str(slot_id)).get()
        if doc.exists:
            return not doc.get("is_occupied")
        return False

    def generate_ereceipt(self, ticket_id: str):
        ticket_data = self.get_ticket_by_id(ticket_id)
        if not ticket_data:
            print("Ticket not found or already exited!")
            return {"status": "failed", "message": "Ticket not found or already exited"}

        slot_id = int(ticket_data["slot_id"])
        vehicle_type = ticket_data["vehicle_type"]
        entry_time = ticket_data["entry_time"]

        # Release slot if still occupied
        if not self.is_slot_released(slot_id):
            print(f"Slot {slot_id} is still occupied! Releasing now...")
            self.slot.release_slot(slot_id)

        # Calculate duration
        try:
            entry_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
        except Exception:
            entry_dt = datetime.now()

        exit_time = datetime.now()
        duration_minutes = (exit_time - entry_dt).total_seconds() / 60
        duration_hours = max(duration_minutes / 60, 0.01)

        # Calculate price and generate receipt
        price = self.receipt.calculate_price(vehicle_type, duration_hours)
        self.receipt.set_exit_time(exit_time.strftime("%Y-%m-%d %H:%M:%S"))
        receipt_text = self.receipt.generate_receipt(ticket_id, slot_id, vehicle_type, entry_dt)

        # Mark ticket as exited in Firestore
        self.update_ticket_exit(ticket_id, exit_time)

        print(receipt_text)
        return {
            "status": "success",
            "receipt": receipt_text,
            "price": price,
            "duration_minutes": duration_minutes
        }

    def update_ticket_exit(self, ticket_id: str, exit_time: datetime):
        """Update the exit_time field on the ticket document."""
        db = get_db()
        db.collection("tickets").document(ticket_id).update({
            "exit_time": exit_time.strftime("%Y-%m-%d %H:%M:%S")
        })
