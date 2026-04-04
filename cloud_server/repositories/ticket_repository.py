from datetime import datetime
from cloud_server.cloud.firestore_database import FirestoreDatabase


class TicketRepository:
    def __init__(self):
        self.db = FirestoreDatabase().get_client()
        self.collection = self.db.collection("tickets")

    def create_ticket(self, ticket_id, vehicle_type, slot_id):
        data = {
            "ticket_id": ticket_id,
            "vehicle_type": vehicle_type,
            "slot_id": slot_id,
            "entry_time": datetime.now().isoformat(),
            "exit_time": None,
            "status": "active",
            "duration_hours": None,
            "amount": None
        }
        self.collection.document(ticket_id).set(data)
        return data

    def get_ticket(self, ticket_id):
        doc = self.collection.document(ticket_id).get()
        return doc.to_dict() if doc.exists else None

    def update_ticket(self, ticket_id, updates: dict):
        self.collection.document(ticket_id).update(updates)

    def close_ticket(self, ticket_id, duration_hours, amount):
        self.collection.document(ticket_id).update({
            "exit_time": datetime.now().isoformat(),
            "status": "closed",
            "duration_hours": duration_hours,
            "amount": amount
        })