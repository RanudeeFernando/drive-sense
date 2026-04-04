import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID", "YOUR_FIREBASE_PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "secrets/firebase_service_account.json"
)