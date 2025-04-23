# app/services/receipt_service.py
from datetime import datetime
from app.database import get_database
from bson import ObjectId

async def save_receipt(receipt_data):
    """Save a new receipt to the database."""
    db = get_database()
    receipt_data["created_at"] = datetime.now()
    receipt_data["updated_at"] = datetime.now()
    
    # Insert receipt
    result = await db.receipts.insert_one(receipt_data)
    return result.inserted_id

async def get_receipt(receipt_id, user_id):
    """Get a specific receipt by ID."""
    db = get_database()
    receipt = await db.receipts.find_one({
        "_id": receipt_id,
        "user_id": user_id
    })
    
    if receipt:
        receipt["id"] = str(receipt["_id"])
        del receipt["_id"]
        return receipt
    
    return None

async def get_user_receipts(user_id, skip=0, limit=20, category=None, date_filters=None):
    """Get all receipts for a user with optional filtering."""
    db = get_database()
    
    # Build query
    query = {"user_id": user_id}
    
    if category:
        query["items.category"] = category
    
    if date_filters:
        query["date"] = {}
        if "start" in date_filters:
            query["date"]["$gte"] = date_filters["start"]
        if "end" in date_filters:
            query["date"]["$lte"] = date_filters["end"]
    
    # Execute query
    cursor = db.receipts.find(query).sort("date", -1).skip(skip).limit(limit)
    
    # Process results
    receipts = []
    async for receipt in cursor:
        receipt["id"] = str(receipt["_id"])
        del receipt["_id"]
        receipts.append(receipt)
    
    return receipts

async def update_receipt(receipt_id, user_id, updates):
    """Update a receipt."""
    db = get_database()
    updates["updated_at"] = datetime.now()
    
    # Update receipt
    result = await db.receipts.update_one(
        {"_id": receipt_id, "user_id": user_id},
        {"$set": updates}
    )
    
    if result.modified_count:
        # Get and return updated receipt
        receipt = await db.receipts.find_one({"_id": receipt_id})
        receipt["id"] = str(receipt["_id"])
        del receipt["_id"]
        return receipt
    
    return None

async def delete_receipt(receipt_id, user_id):
    """Delete a receipt."""
    db = get_database()
    result = await db.receipts.delete_one({
        "_id": receipt_id,
        "user_id": user_id
    })
    
    return result.deleted_count > 0