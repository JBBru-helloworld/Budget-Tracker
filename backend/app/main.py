# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials
import os
from dotenv import load_dotenv
from app.routes.api import api_router
from app.database import connect_to_mongo, close_mongo_connection

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
})

firebase_admin.initialize_app(cred)

# Create FastAPI app
app = FastAPI(title="BudgetTracker API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for avatars and other assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Connect to MongoDB on startup
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

# Close MongoDB connection on shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include API routes
app.include_router(api_router, prefix="/api")

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "BudgetTracker API is running"}