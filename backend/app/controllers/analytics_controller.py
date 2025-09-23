# app/controllers/analytics_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime, timedelta
import calendar
from app.services.receipt_service import get_user_receipts
from app.services.analytics_service import get_spending_summary
from app.services.firebase_service import get_user_id_from_token

router = APIRouter()

@router.get("/")
async def get_analytics(
    user_id: str = Depends(get_user_id_from_token),
    time_range: str = Query("weekly", alias="range")  # weekly, monthly, yearly
):
    """Get analytics data for charts in the format expected by the frontend"""
    try:
        today = datetime.now()
        data = []
        
        if time_range == "weekly":
            # Get last 8 weeks of data
            for i in range(8):
                week_end = today - timedelta(days=7 * i)
                week_start = week_end - timedelta(days=7)
                
                # Get receipts for this week
                receipts = await get_user_receipts(
                    user_id,
                    date_filters={"start": week_start, "end": week_end}
                )
                
                total = sum(receipt.get("total_amount", 0) for receipt in receipts)
                data.append({
                    "period": f"Week {8-i}",
                    "amount": total
                })
                
        elif time_range == "monthly":
            # Get last 12 months of data
            for i in range(12):
                month = today.month - i
                year = today.year
                while month <= 0:
                    month += 12
                    year -= 1
                
                month_start = datetime(year, month, 1)
                last_day = calendar.monthrange(year, month)[1]
                month_end = datetime(year, month, last_day)
                
                # Get receipts for this month
                receipts = await get_user_receipts(
                    user_id,
                    date_filters={"start": month_start, "end": month_end}
                )
                
                total = sum(receipt.get("total_amount", 0) for receipt in receipts)
                data.append({
                    "period": month_start.strftime("%b %Y"),
                    "amount": total
                })
                
        elif time_range == "yearly":
            # Get last 5 years of data
            for i in range(5):
                year = today.year - i
                year_start = datetime(year, 1, 1)
                year_end = datetime(year, 12, 31)
                
                # Get receipts for this year
                receipts = await get_user_receipts(
                    user_id,
                    date_filters={"start": year_start, "end": year_end}
                )
                
                total = sum(receipt.get("total_amount", 0) for receipt in receipts)
                data.append({
                    "period": str(year),
                    "amount": total
                })
        
        # Reverse to get chronological order
        data.reverse()
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analytics: {str(e)}"
        )

@router.get("/spending")
async def get_spending_analytics(
    user_id: str = Depends(get_user_id_from_token),
    time_period: str = "weekly",  # weekly, monthly, yearly
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None
):

    # Get spending analytics for the specified time period
    # Set default date range based on time_period if not explicitly provided
    if not start_date or not end_date:
        today = datetime.now()
        
        if time_period == "weekly":
            # Start from beginning of current week (Monday)
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)  # Sunday
        elif time_period == "monthly":
            # Start from beginning of current month
            start = today.replace(day=1)
            # End at last day of current month
            last_day = calendar.monthrange(today.year, today.month)[1]
            end = today.replace(day=last_day)
        elif time_period == "yearly":
            # Start from beginning of current year
            start = today.replace(month=1, day=1)
            # End at last day of current year
            end = today.replace(month=12, day=31)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time_period. Must be 'weekly', 'monthly', or 'yearly'"
            )
            
        start_date = start.strftime("%Y-%m-%d")
        end_date = end.strftime("%Y-%m-%d")
    
    try:
        # Get spending summary based on date range and category filter
        spending_data = await get_spending_summary(
            user_id,
            datetime.strptime(start_date, "%Y-%m-%d"),
            datetime.strptime(end_date, "%Y-%m-%d"),
            category
        )
        
        return {
            "time_period": time_period,
            "start_date": start_date,
            "end_date": end_date,
            "category": category if category else "all",
            "data": spending_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analytics: {str(e)}"
        )

@router.get("/categories")
async def get_category_breakdown(
    user_id: str = Depends(get_user_id_from_token),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):

    # Get spending breakdown by category
    # Default to current month if dates not provided
    if not start_date or not end_date:
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = today.replace(day=last_day).strftime("%Y-%m-%d")
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get receipts for the date range
        receipts = await get_user_receipts(
            user_id,
            date_filters={"start": start, "end": end}
        )
        
        # Aggregate spending by category
        categories = {}
        for receipt in receipts:
            for item in receipt.get("items", []):
                category = item.get("category", "Uncategorized")
                if category not in categories:
                    categories[category] = 0
                categories[category] += item.get("price", 0)
        
        # Sort categories by amount spent (descending)
        result = [
            {"category": category, "amount": amount}
            for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "categories": result,
            "total": sum(item["amount"] for item in result)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating category breakdown: {str(e)}"
        )