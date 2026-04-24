
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cloud_server.cloud_db.firestore_client import get_db

SLOTS = [
    {"slot_id": "1", "slot_type": "bike",  "is_occupied": False, "distance_start": 61.5, "distance_end": 71.5},
    {"slot_id": "2", "slot_type": "bike",  "is_occupied": False, "distance_start": 51.5, "distance_end": 61.5},
    {"slot_id": "3", "slot_type": "car",   "is_occupied": False, "distance_start": 36.5, "distance_end": 51.5},
    {"slot_id": "4", "slot_type": "car",   "is_occupied": False, "distance_start": 21.5, "distance_end": 36.5},
    {"slot_id": "5", "slot_type": "lorry", "is_occupied": False, "distance_start": 1.5,  "distance_end": 21.5},
]


def seed():
    """
    Adds all predefined slots to the database.

    Each slot from SLOTS is saved using its slot_id, and progress
    is printed as the data is inserted.
    """
    db = get_db()
    for slot in SLOTS:
        db.collection("slots").document(slot["slot_id"]).set(slot)
        print(f"Seeded slot {slot['slot_id']} ({slot['slot_type']})")
    print("\nFirestore seeding complete! You can now delete this file.")


if __name__ == "__main__":
    seed()
