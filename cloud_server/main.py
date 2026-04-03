import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from cloud_server.cloud_api import router

app = FastAPI(title="Smart Parking Cloud API ☁️")

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Smart Parking Cloud Server API Running!"}

if __name__ == "__main__":
    import uvicorn
    # Make sure to run this using `python cloud_server/main.py`
    uvicorn.run("cloud_server.main:app", host="127.0.0.1", port=8000, reload=True)
