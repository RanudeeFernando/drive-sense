import firebase_admin
from firebase_admin import credentials, firestore

from cloud_server.config.settings import (
    FIRESTORE_PROJECT_ID,
    GOOGLE_APPLICATION_CREDENTIALS,
)


class FirestoreDatabase:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
            firebase_admin.initialize_app(cred, {
                "projectId": FIRESTORE_PROJECT_ID
            })

        self.db = firestore.client()

    def get_client(self):
        return self.db