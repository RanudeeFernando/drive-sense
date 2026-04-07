# cloud_server/repositories/light_repository.py
from datetime import datetime
from cloud_server.cloud_db.firestore_client import get_db

class LightRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("light_logs")

    def log_event(self, light_on: bool):
        """Log a light on/off event with a timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event_id = f"LT-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
        
        doc_ref = self.collection.document(event_id)
        doc_ref.set({
            "timestamp": timestamp,
            "status": "ON" if light_on else "OFF"
        })
        return event_id

    def get_all_logs(self):
        """Return all light logs from Firestore, ordered by timestamp descending."""
        docs = self.collection.order_by("timestamp", direction="DESCENDING").stream()
        logs = []
        for doc in docs:
            logs.append(doc.to_dict())
        return logs
