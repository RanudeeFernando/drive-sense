import os
import shutil
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load .env file for local development (no effect on EC2 where env vars are set via IAM Role/systemd)
load_dotenv(override=False)

# Import Heavy Logic Elements
from cloud.cloud_database import CloudDatabase
from ml_models.classifier import VehicleClassificationModel
from core.parking_manager import ParkingManager
from data_models.parking_slot import ParkingSlot

app = FastAPI(title="DriveSense Cloud Server")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# CLOUD INITIALIZATION
# =========================================================
print("\n[CLOUD INIT] Connecting to AWS DynamoDB...")
cloud_db = CloudDatabase("ParkingSlots")

print("[CLOUD INIT] Loading Deep Learning Model into Server Memory...")
classifier = VehicleClassificationModel("models/vehicle_classifier_model.h5")
classifier.load_model()

# Setup Virtual Parking Manager Logic
slots = [
    ParkingSlot(1, "bike", 2.0, 1.0),
    ParkingSlot(2, "car", 4.5, 2.0),
    ParkingSlot(3, "car", 4.5, 2.0),
    ParkingSlot(4, "lorry", 8.0, 3.0),
    ParkingSlot(5, "car", 4.5, 2.0),
]
parking_manager = ParkingManager(slots)

print("[CLOUD INIT] Syncing initial slot states to AWS DynamoDB...\n")
for slot in slots:
    cloud_db.update_data(slot.slot_id, {
        "type": slot.slot_type,
        "is_occupied": slot.slot_status
    })

# =========================================================
# CLOUD ROUTES
# =========================================================
@app.get("/api/slots")
def get_slots():
    """Returns real-time slot data from DynamoDB for the React UI."""
    return cloud_db.retrieve()

@app.post("/api/detect_vehicle")
async def detect_vehicle(image: UploadFile = File(...)):
    """
    Receives an image from the Edge Device, runs inference, manages the parking slot,
    updates AWS, and returns an actionable hardware command back to the Edge.
    """
    # Create temp directory for incoming images
    os.makedirs("cloud_temp", exist_ok=True)
    temp_file_path = os.path.join("cloud_temp", image.filename)
    
    # Save the uploaded edge image to server disk temporarily
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
        
    try:
        # A. CLOUD INFERENCE: Neural Network processing
        vehicle_type = classifier.classify_vehicle(temp_file_path)
        
        # B. CLOUD LOGIC: Allocate a Slot
        ticket = parking_manager.vehicle_entry(vehicle_type)
        if ticket:
            # C. CLOUD DATACENTER: Update AWS NoSQL Table
            cloud_db.update_data(f"Ticket_{ticket.ticket_id}", ticket.generate_ticket())
            
            for slot in slots:
                if slot.slot_id == ticket.slot_id:
                    cloud_db.update_data(str(slot.slot_id), {
                        "type": slot.slot_type,
                        "is_occupied": True,
                        "ticket_id": ticket.ticket_id
                    })
                    break
            
            os.remove(temp_file_path) # cleanup
            
            # D. CLOUD COMMAND: Tell the Edge what physical action to take!
            return {
                "status": "success",
                "command": "OPEN_BARRIER",
                "assigned_slot": ticket.slot_id,
                "vehicle_type": vehicle_type,
                "ticket_id": ticket.ticket_id
            }
        else:
            os.remove(temp_file_path)
            return {
                "status": "full",
                "command": "DISPLAY_FULL_MESSAGE",
                "vehicle_type": vehicle_type
            }
            
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
