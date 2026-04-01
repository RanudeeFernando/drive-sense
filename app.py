'''# app.py

from fastapi import FastAPI
from api import router

app = FastAPI(title="Smart Parking API 🚗")

# Include routes
app.include_router(router)


@app.get("/")
def home():
    return {"message": "Smart Parking System API Running"}'''

# app.py

from fastapi import FastAPI
from api import router

app = FastAPI(title="Smart Parking API 🚗")

# Include routes
app.include_router(router)


@app.get("/")
def home():
    return {"message": "Smart Parking System API Running"}


# 👇 This lets you run with: python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)