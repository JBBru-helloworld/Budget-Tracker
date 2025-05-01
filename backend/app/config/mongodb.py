from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://127.0.0.1:27017/')
DB_NAME = os.getenv('MONGODB_DB_NAME', 'budget_tracker')

def get_database():
    """
    Returns a MongoDB database instance
    """
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        # Verify the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return db
    except ServerSelectionTimeoutError as e:
        print(f"Failed to connect to MongoDB. Error: {e}")
        raise

# Create a global database instance
db = get_database() 