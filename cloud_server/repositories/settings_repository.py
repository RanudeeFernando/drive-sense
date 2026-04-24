
from cloud_server.cloud_db.firestore_client import get_db

class SettingsRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("settings")
        self.doc_id = "ldr_control"

    def get_ldr_enabled(self) -> bool:
        """Fetch the LDR enabled status from Firestore."""
        doc = self.collection.document(self.doc_id).get()
        if doc.exists:
            return doc.to_dict().get("enabled", True)
        return True

    def set_ldr_enabled(self, enabled: bool) -> None:
        """Update the LDR enabled status in Firestore."""
        self.collection.document(self.doc_id).set({"enabled": enabled}, merge=True)
