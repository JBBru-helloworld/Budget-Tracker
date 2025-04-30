# app/services/receipt_service.py
from datetime import datetime
from app.database import get_database
from bson import ObjectId
from typing import List, Dict
from app.models.receipt_model import Receipt, ReceiptItem, SharedExpense

async def save_receipt(receipt_data: dict):
    """Save a new receipt to the database."""
    db = await get_database()
    receipt_data["created_at"] = datetime.now()
    receipt_data["updated_at"] = datetime.now()
    
    # Process shared expenses
    if receipt_data.get("is_shared"):
        receipt_data["shared_expenses"] = await _calculate_shared_expenses(receipt_data["items"])
    
    # Insert receipt
    result = await db.receipts.insert_one(receipt_data)
    return str(result.inserted_id)

async def _calculate_shared_expenses(items: List[ReceiptItem]) -> List[SharedExpense]:
    """Calculate shared expenses based on item assignments."""
    shared_expenses: Dict[str, SharedExpense] = {}
    
    for item in items:
        if item.assigned_to:
            if item.assigned_to not in shared_expenses:
                shared_expenses[item.assigned_to] = SharedExpense(
                    user_id=item.assigned_to,
                    amount=0,
                    items=[]
                )
            shared_expenses[item.assigned_to].amount += item.price
            shared_expenses[item.assigned_to].items.append(item.id)
    
    return list(shared_expenses.values())

async def assign_items_to_user(receipt_id: str, user_id: str, item_ids: List[str], target_user_id: str):
    """Assign items to a specific user."""
    db = await get_database()
    
    # Get the receipt
    receipt = await db.receipts.find_one({
        "_id": ObjectId(receipt_id),
        "user_id": user_id
    })
    
    if not receipt:
        raise ValueError("Receipt not found")
    
    # Update item assignments
    for item in receipt["items"]:
        if str(item["_id"]) in item_ids:
            item["assigned_to"] = target_user_id
    
    # Recalculate shared expenses
    receipt["is_shared"] = True
    receipt["shared_expenses"] = await _calculate_shared_expenses(receipt["items"])
    receipt["updated_at"] = datetime.now()
    
    # Update the receipt
    await db.receipts.update_one(
        {"_id": ObjectId(receipt_id)},
        {"$set": receipt}
    )
    
    return await get_receipt(receipt_id, user_id)

async def get_receipt(receipt_id: str, user_id: str):
    """Get a specific receipt by ID."""
    db = await get_database()
    receipt = await db.receipts.find_one({
        "_id": ObjectId(receipt_id),
        "$or": [
            {"user_id": user_id},
            {"shared_expenses.user_id": user_id}
        ]
    })
    
    if receipt:
        receipt["id"] = str(receipt["_id"])
        del receipt["_id"]
        return receipt
    
    return None

async def get_user_receipts(user_id: str, skip: int = 0, limit: int = 20, category: str = None, date_filters: dict = None):
    """Get all receipts for a user with optional filtering."""
    db = await get_database()
    
    # Build query
    query = {
        "$or": [
            {"user_id": user_id},
            {"shared_expenses.user_id": user_id}
        ]
    }
    
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

async def update_receipt(receipt_id: str, user_id: str, updates: dict):
    """Update a receipt."""
    db = await get_database()
    updates["updated_at"] = datetime.now()
    
    # If items are updated, recalculate shared expenses
    if "items" in updates:
        updates["shared_expenses"] = await _calculate_shared_expenses(updates["items"])
    
    # Update receipt
    result = await db.receipts.update_one(
        {"_id": ObjectId(receipt_id), "user_id": user_id},
        {"$set": updates}
    )
    
    if result.modified_count:
        # Get and return updated receipt
        receipt = await db.receipts.find_one({"_id": ObjectId(receipt_id)})
        receipt["id"] = str(receipt["_id"])
        del receipt["_id"]
        return receipt
    
    return None

async def delete_receipt(receipt_id: str, user_id: str):
    """Delete a receipt."""
    db = await get_database()
    result = await db.receipts.delete_one({
        "_id": ObjectId(receipt_id),
        "user_id": user_id
    })
    
    return result.deleted_count > 0