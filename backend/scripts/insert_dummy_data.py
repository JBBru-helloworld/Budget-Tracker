from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from bson import ObjectId
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK with your service account
cred = credentials.Certificate('budget-tracker-bbdf7-firebase-adminsdk-fbsvc-146f301fb9.json')
firebase_admin.initialize_app(cred)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["budget_tracker"]

# Get or create user profile
EMAIL = "jb.brubusiness3@gmail.com"

# Try to get Firebase user
try:
    firebase_user = auth.get_user_by_email(EMAIL)
    USER_ID = firebase_user.uid
except:
    print(f"User with email {EMAIL} not found in Firebase")
    exit(1)

# Check if user profile exists in MongoDB
user_profile = db.user_profiles.find_one({"email": EMAIL})
if not user_profile:
    user_profile = {
        "user_id": USER_ID,
        "email": EMAIL,
        "display_name": "Joshua",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "budget_targets": {}
    }
    db.user_profiles.insert_one(user_profile)

# Categories with modern UI colors and icons
categories = [
    {"name": "Groceries", "color": "#10B981", "icon": "shopping-cart"},
    {"name": "Dining Out", "color": "#F59E0B", "icon": "utensils"},
    {"name": "Transportation", "color": "#3B82F6", "icon": "car"},
    {"name": "Entertainment", "color": "#8B5CF6", "icon": "film"},
    {"name": "Utilities", "color": "#EC4899", "icon": "bolt"},
    {"name": "Shopping", "color": "#6366F1", "icon": "bag"},
    {"name": "Health", "color": "#EF4444", "icon": "heart"},
    {"name": "Education", "color": "#14B8A6", "icon": "book"},
]

# Store names
stores = [
    "Walmart", "Target", "Kroger", "Whole Foods", "Trader Joe's",
    "McDonald's", "Starbucks", "Chipotle", "Pizza Hut", "Subway",
    "Shell", "Exxon", "BP", "7-Eleven", "CVS",
    "Netflix", "Spotify", "Amazon Prime", "Hulu", "Disney+",
]

# Insert categories
db.categories.delete_many({"user_id": USER_ID})
for category in categories:
    category["user_id"] = USER_ID
    category["created_at"] = datetime.now()
    category["updated_at"] = datetime.now()
db.categories.insert_many(categories)

# Get category IDs
category_ids = [str(cat["_id"]) for cat in db.categories.find({"user_id": USER_ID})]

# Generate dummy receipts
db.receipts.delete_many({"user_id": USER_ID})
receipts = []

# Generate receipts for the last 90 days
for i in range(50):
    date = datetime.now() - timedelta(days=random.randint(0, 90))
    store = random.choice(stores)
    total_amount = round(random.uniform(10, 200), 2)
    
    # Generate 2-5 items per receipt
    num_items = random.randint(2, 5)
    items = []
    remaining_amount = total_amount
    
    for j in range(num_items):
        if j == num_items - 1:
            item_amount = remaining_amount
        else:
            item_amount = round(random.uniform(5, remaining_amount / 2), 2)
            remaining_amount -= item_amount
        
        items.append({
            "name": f"Item {j+1}",
            "price": item_amount,
            "quantity": random.randint(1, 3),
            "category": random.choice(category_ids),
            "assigned_to": None,
            "shared_with": []
        })
    
    receipt = {
        "user_id": USER_ID,
        "date": date,
        "total_amount": total_amount,
        "store_name": store,
        "items": items,
        "image_url": None,  # No dummy images
        "created_at": date,
        "updated_at": date,
        "is_shared": False,
        "shared_expenses": []
    }
    
    receipts.append(receipt)

db.receipts.insert_many(receipts)

# Set budget targets
budget_targets = {
    "Groceries": 500,
    "Dining Out": 300,
    "Transportation": 200,
    "Entertainment": 150,
    "Utilities": 250,
    "Shopping": 300,
    "Health": 200,
    "Education": 100
}

# Update user profile with budget targets
db.user_profiles.update_one(
    {"user_id": USER_ID},
    {"$set": {
        "budget_targets": budget_targets,
        "updated_at": datetime.now()
    }}
)

print("Dummy data inserted successfully!")
print(f"- User profile created/updated for {EMAIL}")
print(f"- {len(categories)} categories created")
print(f"- {len(receipts)} receipts created")
print(f"- Budget targets set for {len(budget_targets)} categories")