# app/database.py
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection details - FIX THE NAMING!
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "budget_tracker")  # Changed from DB_NAME

# MongoDB client
client = None
db = None

async def connect_to_mongo():
    """Connect to MongoDB."""
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]  # Also changed here
    print(f"Connected to MongoDB: {MONGODB_URI}/{MONGODB_DB_NAME}")

async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")

def get_database():
    """Get database instance."""
    return db