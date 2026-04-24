
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cloud_server.cloud_db.firestore_client import get_db

ADMINS = [
    {"username": "Thehara", "password": "theh"},
]


def seed():
    """
    Seed the "admins" collection with predefined admin users.
    Uses usernames as document IDs and prints progress messages.
    """
    db = get_db()
    for admin in ADMINS:
        db.collection("admins").document(admin["username"]).set(admin)
        print(f"[OK] Seeded admin: {admin['username']}")
    print("\nAdmins seeding complete!")


if __name__ == "__main__":
    seed()
