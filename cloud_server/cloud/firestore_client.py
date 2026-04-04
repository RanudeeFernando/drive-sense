import os
import firebase_admin
from firebase_admin import credentials, firestore

_db = None


def get_db():
    """Returns a singleton Firestore client pointing to drive-sense-db."""
    global _db
    if _db is None:
        if not firebase_admin._apps:
            cred_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "credentials",
                "serviceAccountKey.json"
            )
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _db = firestore.client(database_id="drive-sense-db")
    return _db
