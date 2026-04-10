import os
import firebase_admin
from firebase_admin import credentials, firestore

_db = None


def get_db():
    """
    Returns a singleton Firestore client.
    Uses the same drive-sense-db database.
    """
    global _db

    if _db is None:
        if not firebase_admin._apps:
            # Adjust path relative to raspberry_pi folder
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            cred_path = os.path.join(
                base_dir,
                "credentials",
                "serviceAccountKey.json"
            )

            if not os.path.exists(cred_path):
                raise FileNotFoundError(
                    f"Firestore credential file not found at: {cred_path}"
                )

            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        _db = firestore.client(database_id="drive-sense-db")

    return _db