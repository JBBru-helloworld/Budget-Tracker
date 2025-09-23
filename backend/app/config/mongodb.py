# app/database.py
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "budget_tracker")

# MongoDB client - use a class to manage state better
class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self._connected = False
    
    async def connect(self):
        """Connect to MongoDB."""
        if not self._connected:
            self.client = AsyncIOMotorClient(MONGODB_URI)
            self.db = self.client[MONGODB_DB_NAME]
            self._connected = True
            print(f"Connected to MongoDB: {MONGODB_URI}/{MONGODB_DB_NAME}")
    
    async def close(self):
        """Close MongoDB connection."""
        if self.client and self._connected:
            self.client.close()
            self._connected = False
            print("Closed MongoDB connection")
    
    def get_database(self):
        """Get database instance."""
        if not self._connected or self.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db

# Global instance
db_manager = DatabaseManager()

async def connect_to_mongo():
    """Connect to MongoDB."""
    await db_manager.connect()

async def close_mongo_connection():
    """Close MongoDB connection."""
    await db_manager.close()

def get_database():
    """Get database instance."""
    return db_manager.get_database()