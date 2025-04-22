# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from .routes import auth, receipts, analytics, tips
from .middleware.auth_middleware import auth_middleware
from .config import settings

# Load environment variables
load_dotenv()

# Lifespan context for database connections and cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    from motor.motor_asyncio import AsyncIOMotorClient
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.mongodb = app.mongodb_client[settings.MONGODB_DB_NAME]
    print("Connected to MongoDB")
    
    yield
    
    # Shutdown: Close MongoDB connection
    app.mongodb_client.close()
    print("MongoDB connection closed")

# Create FastAPI app
app = FastAPI(lifespan=lifespan, title="Budget Tracker API", description="API for budget tracking application")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.middleware("http")(auth_middleware)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["Receipts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(tips.router, prefix="/api/tips", tags=["Tips"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Budget Tracker API"}