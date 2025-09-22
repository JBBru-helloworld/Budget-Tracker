# app/controllers/dashboard_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth_middleware import get_current_user
from app.services.receipt_service import get_user_receipts
from typing import Dict, Any
import datetime

router = APIRouter()

@router.get("/")
async def get_dashboard_data(
    current_user: dict = Depends(get_current_user)
):
    """
    Get dashboard summary data for the user
    """
    try:
        user_id = current_user["uid"]
        
        # Get current month's data
        now = datetime.datetime.now()
        start_of_month = datetime.datetime(now.year, now.month, 1)
        
        # Get recent receipts/transactions
        receipts = await get_user_receipts(user_id, limit=10)
        
        # Convert receipts to transaction format for dashboard
        transactions = []
        total_spent = 0.0
        
        for receipt in receipts:
            # Create transaction from receipt data
            transaction = {
                "_id": str(receipt.get('id', '')),
                "description": f"Purchase at {receipt.get('store', 'Unknown Store')}",
                "category": receipt.get('category', 'Other'),
                "amount": -float(receipt.get('amount', 0)),  # Negative for expenses
                "date": receipt.get('date').isoformat() if receipt.get('date') and hasattr(receipt.get('date'), 'isoformat') else str(receipt.get('date', ''))
            }
            transactions.append(transaction)
            total_spent += float(receipt.get('amount', 0))
        
        # Get budget (for now, use a default - you can implement user budget settings later)
        budget = 1000.0  # Default budget, can be made configurable
        
        return {
            "transactions": transactions[:10],  # Limit to 10 most recent
            "budget": budget,
            "total_spent": total_spent
        }
        
    except Exception as e:
        print(f"Dashboard error: {str(e)}")  # Debug logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )

@router.post("/budget")
async def set_user_budget(
    budget_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Set user's monthly budget
    """
    try:
        amount = budget_data.get("amount", 0)
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget amount must be greater than 0"
            )
        
        # For now, just return success
        # In a real app, you'd save this to a user settings collection
        return {
            "message": "Budget updated successfully",
            "amount": amount
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting budget: {str(e)}"
        )
