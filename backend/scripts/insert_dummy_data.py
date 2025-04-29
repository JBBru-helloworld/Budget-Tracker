from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["budget_tracker"]

# Dummy user ID (replace with your actual user ID from Firebase)
USER_ID = "dummy_user_123"

# Categories
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

for i in range(50):  # Generate 50 receipts
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
        "image_url": f"https://example.com/receipts/{i}.jpg",
        "created_at": date,
        "updated_at": date,
        "is_shared": random.choice([True, False]),
        "shared_expenses": []
    }
    
    receipts.append(receipt)

db.receipts.insert_many(receipts)

print("Dummy data inserted successfully!")
print(f"- {len(categories)} categories created")
print(f"- {len(receipts)} receipts created") 