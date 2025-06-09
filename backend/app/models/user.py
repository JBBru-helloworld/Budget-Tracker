from datetime import datetime
from bson import ObjectId
from ..config.mongodb import db

users_collection = db['users']

class User:
    def __init__(self, username, email, password_hash, created_at=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def create_user(username, email, password_hash):
        # Create a new user
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.utcnow()
        }
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def get_user_by_id(user_id):
        # Get user by ID
        try:
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            return user
        except:
            return None

    @staticmethod
    def get_user_by_email(email):
        # Get user by email
        return users_collection.find_one({'email': email})

    @staticmethod
    def update_user(user_id, update_data):
        # Update user information
        try:
            result = users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False

    @staticmethod
    def delete_user(user_id):
        # Delete user
        try:
            result = users_collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except:
            return False 