import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from raspberry_pi.pi_api import router

"""
Entry point for Raspberry Pi FastAPI server.
Initializes the API app, CORS configuration, and registers routers.
Runs the local edge API service for sensor and UI communication.
"""

app = FastAPI(title="Smart Parking Raspberry Pi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("raspberry_pi.pi_api_main:app", host="127.0.0.1", port=8001, reload=True)