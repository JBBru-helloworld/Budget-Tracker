# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.routes.api import api_router
from app.config.mongodb import connect_to_mongo, close_mongo_connection
from app.routes import receipts
from app.routes import notifications

# Create FastAPI app
app = FastAPI(title="BudgetTracker API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for avatars and other assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api")
app.include_router(receipts.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")

# Add database connection event handlers
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "BudgetTracker API is running"}