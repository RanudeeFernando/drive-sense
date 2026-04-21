import sys
import os
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler # type: ignore
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cloud_server.cloud_api import router

app = FastAPI(title="Smart Parking Cloud API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Smart Parking Cloud Server API Running!"}

def run_model_training():
    print("Starting scheduled tasks...")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploader_script_path = os.path.join(project_root, "uploader.py")
    model_script_path = os.path.join(project_root, "model_train", "model.py")
    
    print("Running uploader...")
    try:
        subprocess.run([sys.executable, uploader_script_path], check=True)
        print("Uploader completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Uploader failed with error: {e}")
    except Exception as e:
        print(f"Unexpected error during uploader: {e}")

    print("Starting scheduled model training...")
    try:
        subprocess.run([sys.executable, model_script_path], check=True)
        print("Model training completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Model training failed with error: {e}")
    except Exception as e:
        print(f"Unexpected error during model training: {e}")

scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    run_model_training()
    #scheduler.add_job(run_model_training, 'interval', days=30)
    scheduler.start()
    print("Scheduler started. Model training scheduled to run every 30 days.")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()
    print("Scheduler shutdown.")

if __name__ == "__main__":
    import uvicorn
    # Make sure to run this using `python cloud_server/main.py`
    uvicorn.run("cloud_server.main:app", host="127.0.0.1", port=8000, reload=True)