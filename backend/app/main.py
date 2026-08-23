from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api import auth
import os

app = FastAPI(
    title="Luneria CRM API",
    description="Internal CRM system for Luneria agency",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.api.router import api_router

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix="/api/v1")
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Luneria CRM API"}
