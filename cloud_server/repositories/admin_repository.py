
from cloud_server.cloud_db.firestore_client import get_db
from cloud_server.data_models.admin import Admin


class AdminRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection("admins")

    @staticmethod
    def _doc_to_admin(doc) -> Admin:
        data = doc.to_dict()
        return Admin(
            username=data["username"],
            password=data["password"],
        )

    def get_admin_by_username(self, username: str):
        """Fetch an Admin object by username, or None if not found."""
        docs = (
            self.collection
            .where("username", "==", username)
            .limit(1)
            .stream()
        )
        for doc in docs:
            return self._doc_to_admin(doc)
        return None

    def verify_credentials(self, username: str, password: str) -> bool:
        """Return True if the username/password pair exists in Firestore."""
        admin = self.get_admin_by_username(username)
        if admin is None:
            return False
        return admin.get_password() == password
