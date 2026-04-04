from cloud_server.cloud.firestore_database import FirestoreDatabase


class SettingsRepository:
    def __init__(self):
        self.db = FirestoreDatabase().get_client()
        self.collection = self.db.collection("settings")
        self.doc_id = "lighting"

    def get_light_settings(self):
        doc = self.collection.document(self.doc_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def update_light_settings(self, data):
        self.collection.document(self.doc_id).set(data, merge=True)

    def initialize_default_light_settings(self):
        doc = self.collection.document(self.doc_id).get()
        if not doc.exists:
            self.collection.document(self.doc_id).set({
                "mode": "AUTO",
                "threshold": 15,
                "light_on": False
            })