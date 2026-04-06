# cloud_server/data/seed_settings.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cloud_server.cloud_db.firestore_client import get_db

def seed():
    db = get_db()
    db.collection("settings").document("ldr_control").set({"enabled": True})
    print("[OK] Seeded settings: ldr_control enabled=True")

if __name__ == "__main__":
    seed()
