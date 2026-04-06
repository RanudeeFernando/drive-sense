"""
seed_admins.py — Run ONCE to populate the admins collection in Firestore.

Usage:
    python -m cloud_server.data.seed_admins

After running successfully, you can keep this file for adding new admins later.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cloud_server.cloud_db.firestore_client import get_db

ADMINS = [
    {"username": "Thehara", "password": "theh"},
]


def seed():
    db = get_db()
    for admin in ADMINS:
        db.collection("admins").document(admin["username"]).set(admin)
        print(f"[OK] Seeded admin: {admin['username']}")
    print("\nAdmins seeding complete!")


if __name__ == "__main__":
    seed()
