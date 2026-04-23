"""
seed_firestore.py — Run ONCE to populate the slots collection.

Usage:
    python -m cloud_server.data.seed_firestore

After running successfully, this file can be deleted.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cloud_server.cloud_db.firestore_client import get_db

SLOTS = [
    {"slot_id": "1", "slot_type": "bike",  "slot_length": 2.0,  "slot_width": 1.0,  "is_occupied": False, "distance_start": 1,  "distance_end": 4},
    {"slot_id": "2", "slot_type": "bike",  "slot_length": 2.0,  "slot_width": 1.0,  "is_occupied": False, "distance_start": 5,  "distance_end": 8},
    {"slot_id": "3", "slot_type": "car",   "slot_length": 5.0,  "slot_width": 2.5,  "is_occupied": False, "distance_start": 9,  "distance_end": 12},
    {"slot_id": "4", "slot_type": "car",   "slot_length": 5.0,  "slot_width": 2.5,  "is_occupied": False, "distance_start": 13, "distance_end": 16},
    {"slot_id": "5", "slot_type": "lorry", "slot_length": 10.0, "slot_width": 3.5,  "is_occupied": False, "distance_start": 17, "distance_end": 20},
]


def seed():
    db = get_db()
    for slot in SLOTS:
        db.collection("slots").document(slot["slot_id"]).set(slot)
        print(f"Seeded slot {slot['slot_id']} ({slot['slot_type']})")
    print("\nFirestore seeding complete! You can now delete this file.")


if __name__ == "__main__":
    seed()
