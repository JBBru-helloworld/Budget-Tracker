# backend/app/routes/analytics.py
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.models import ExpenseSummary, Category
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from calendar import monthrange

router = APIRouter()
security = HTTPBearer()

@router.get("/summary")
async def get_spending_summary(
    request: Request,
    period: str = Query(..., enum=["week", "month", "year"]),
    start_date: Optional[str] = None,  # Format: YYYY-MM-DD
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get spending summary for a specified period
    """
    try:
        user_id = request.state.user_id
        
        # Calculate date range
        end_date = datetime.now()
        
        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            # Default periods
            if period == "week":
                start = end_date - timedelta(days=7)
            elif period == "month":
                start = datetime(end_date.year, end_date.month, 1)
            elif period == "year":
                start = datetime(end_date.year, 1, 1)
        
        # Query database for receipts in the date range
        receipts = []
        cursor = request.app.mongodb["receipts"].find({
            "user_id": user_id,
            "date": {"$gte": start, "$lte": end_date}
        })
        async for receipt in cursor:
            receipts.append(receipt)
        
        # Calculate totals by category
        total_amount = 0
        by_category = {cat.value: 0 for cat in Category}
        
        for receipt in receipts:
            total_amount += receipt["total_amount"]
            
            for item in receipt["items"]:
                category = item["category"]
                if category in by_category:
                    item_total = item["price"] * item.get("quantity", 1)
                    by_category[category] += item_total
        
        # Remove categories with zero spending
        by_category = {k: v for k, v in by_category.items() if v > 0}
        
        summary = ExpenseSummary(
            period=period,
            start_date=start,
            end_date=end_date,
            total_amount=total_amount,
            by_category=by_category
        )
        
        return summary.dict()
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating spending summary: {str(e)}"
        )

@router.get("/trends")
async def get_spending_trends(
    request: Request,
    period: str = Query(..., enum=["weekly", "monthly", "yearly"]),
    limit: int = Query(12, ge=1, le=52),  # Number of periods to return
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get spending trends over time for charts
    """
    try:
        user_id = request.state.user_id
        
        end_date = datetime.now()
        periods = []
        trends = []
        
        # Generate periods
        if period == "weekly":
            for i in range(limit):
                period_end = end_date - timedelta(days=7 * i)
                period_start = period_end - timedelta(days=7)
                periods.append((period_start, period_end, f"Week {limit - i}"))
                
        elif period == "monthly":
            for i in range(limit):
                # Get last day of month
                month = end_date.month - i
                year = end_date.year
                while month <= 0:
                    month += 12
                    year -= 1
                
                last_day = monthrange(year, month)[1]
                period_end = datetime(year, month, last_day)
                period_start = datetime(year, month, 1)
                periods.append((period_start, period_end, f"{period_start.strftime('%b %Y')}"))
                
        elif period == "yearly":
            for i in range(limit):
                year = end_date.year - i
                period_end = datetime(year, 12, 31)
                period_start = datetime(year, 1, 1)
                periods.append((period_start, period_end, str(year)))
        
        # Get spending for each period
        for period_start, period_end, label in periods:
            # Query database for receipts in this period
            total = 0
            by_category = {cat.value: 0 for cat in Category}
            
            cursor = request.app.mongodb["receipts"].find({
                "user_id": user_id,
                "date": {"$gte": period_start, "$lte": period_end}
            })
            
            async for receipt in cursor:
                total += receipt["total_amount"]
                
                for item in receipt["items"]:
                    category = item["category"]
                    if category in by_category:
                        item_total = item["price"] * item.get("quantity", 1)
                        by_category[category] += item_total
            
            # Remove categories with zero spending
            by_category = {k: v for k, v in by_category.items() if v > 0}
            
            trends.append({
                "label": label,
                "total": total,
                "by_category": by_category
            })
        
        # Reverse to get chronological order
        trends.reverse()
        
        return trends
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating spending trends: {str(e)}"
        )

@router.get("/budget-comparison")
async def get_budget_comparison(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Compare current month's spending with budget targets
    """
    try:
        user_id = request.state.user_id
        
        # Get user profile with budget targets
        user_profile = await request.app.mongodb["user_profiles"].find_one({"user_id": user_id})
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
            
        budget_targets = user_profile.get("budget_targets", {})
        
        # Calculate current month's spending
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        # Query database for receipts in current month
        spending_by_category = {cat.value: 0 for cat in Category}
        cursor = request.app.mongodb["receipts"].find({
            "user_id": user_id,
            "date": {"$gte": start_of_month, "$lte": now}
        })
        
        async for receipt in cursor:
            for item in receipt["items"]:
                category = item["category"]
                if category in spending_by_category:
                    item_total = item["price"] * item.get("quantity", 1)
                    spending_by_category[category] += item_total
        
        # Create comparison data
        comparison = []
        for category, budget in budget_targets.items():
            if category in spending_by_category:
                spent = spending_by_category[category]
                remaining = budget - spent
                percentage = (spent / budget) * 100 if budget > 0 else 0
                
                comparison.append({
                    "category": category,
                    "budget": budget,
                    "spent": spent,
                    "remaining": remaining,
                    "percentage": percentage
                })
        
        return comparison
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating budget comparison: {str(e)}"
        )