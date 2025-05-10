# app/services/analytics_service.py
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.config.mongodb import get_database
from app.models.receipt_model import ReceiptItem
import statistics
from collections import defaultdict

async def get_spending_summary(user_id: str, start_date: datetime, end_date: datetime, category: Optional[str] = None):
    """Get comprehensive spending summary for a specific date range."""
    db = await get_database()
    
    # Build pipeline for aggregation
    match_stage = {
        "$or": [
            {"user_id": user_id},
            {"shared_expenses.user_id": user_id}
        ],
        "date": {"$gte": start_date, "$lte": end_date}
    }
    
    if category:
        match_stage["items.category"] = category
    
    # Determine group interval based on date range
    days_diff = (end_date - start_date).days
    
    if days_diff <= 7:
        # Daily grouping for weekly view
        group_format = "%Y-%m-%d"
        date_format = "$date"
    elif days_diff <= 31:
        # Daily grouping for monthly view
        group_format = "%Y-%m-%d"
        date_format = "$date"
    else:
        # Monthly grouping for yearly view
        group_format = "%Y-%m"
        date_format = {"$dateToString": {"format": "%Y-%m", "date": "$date"}}
    
    pipeline = [
        {"$match": match_stage},
        {"$unwind": "$items"},
    ]
    
    if category:
        pipeline.append({"$match": {"items.category": category}})
    
    pipeline.extend([
        {"$group": {
            "_id": date_format,
            "total": {"$sum": "$items.price"},
            "items": {"$push": "$items"},
            "categories": {"$addToSet": "$items.category"}
        }},
        {"$sort": {"_id": 1}}
    ])
    
    # Execute aggregation
    results = await db.receipts.aggregate(pipeline).to_list(length=None)
    
    # Process results
    spending_data = []
    category_totals = defaultdict(float)
    all_items = []
    
    for result in results:
        date_str = result["_id"]
        total = result["total"]
        
        # Add to spending data
        spending_data.append({
            "date": date_str,
            "amount": total,
            "categories": list(result["categories"])
        })
        
        # Track category totals
        for item in result["items"]:
            category_totals[item["category"]] += item["price"]
            all_items.append(item)
    
    # Calculate statistics
    daily_totals = [item["amount"] for item in spending_data]
    avg_daily_spending = statistics.mean(daily_totals) if daily_totals else 0
    max_daily_spending = max(daily_totals) if daily_totals else 0
    
    # Generate spending insights
    insights = await _generate_spending_insights(all_items, category_totals)
    
    # Generate spending predictions
    predictions = await _generate_spending_predictions(spending_data)
    
    return {
        "spending_data": spending_data,
        "category_totals": dict(category_totals),
        "statistics": {
            "average_daily_spending": avg_daily_spending,
            "max_daily_spending": max_daily_spending,
            "total_spending": sum(daily_totals)
        },
        "insights": insights,
        "predictions": predictions
    }

async def _generate_spending_insights(items: List[Dict], category_totals: Dict[str, float]) -> Dict:
    """Generate insights about spending patterns."""
    insights = {
        "top_categories": [],
        "spending_trends": [],
        "savings_opportunities": []
    }
    
    # Sort categories by total spending
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Top categories
    insights["top_categories"] = [
        {"category": category, "amount": amount}
        for category, amount in sorted_categories[:3]
    ]
    
    # Analyze spending trends
    daily_spending = defaultdict(float)
    for item in items:
        date = item["date"].strftime("%Y-%m-%d")
        daily_spending[date] += item["price"]
    
    # Calculate weekly trends
    weekly_totals = defaultdict(float)
    for date, amount in daily_spending.items():
        week_start = datetime.strptime(date, "%Y-%m-%d") - timedelta(days=datetime.strptime(date, "%Y-%m-%d").weekday())
        weekly_totals[week_start.strftime("%Y-%m-%d")] += amount
    
    # Identify trends
    weekly_amounts = list(weekly_totals.values())
    if len(weekly_amounts) > 1:
        trend = "increasing" if weekly_amounts[-1] > weekly_amounts[-2] else "decreasing"
        insights["spending_trends"].append({
            "trend": trend,
            "change_percentage": abs((weekly_amounts[-1] - weekly_amounts[-2]) / weekly_amounts[-2] * 100)
        })
    
    # Identify savings opportunities
    for category, amount in sorted_categories:
        if amount > 100:  # Only suggest savings for significant spending
            insights["savings_opportunities"].append({
                "category": category,
                "current_spending": amount,
                "potential_savings": amount * 0.1  # Assume 10% potential savings
            })
    
    return insights

async def _generate_spending_predictions(spending_data: List[Dict]) -> Dict:
    """Generate spending predictions based on historical data."""
    predictions = {
        "next_week": None,
        "next_month": None,
        "trend": None
    }
    
    if len(spending_data) < 7:
        return predictions
    
    # Calculate daily averages
    daily_amounts = [item["amount"] for item in spending_data]
    avg_daily = statistics.mean(daily_amounts)
    
    # Predict next week
    predictions["next_week"] = {
        "estimated_total": avg_daily * 7,
        "confidence": "medium"
    }
    
    # Predict next month
    predictions["next_month"] = {
        "estimated_total": avg_daily * 30,
        "confidence": "low"
    }
    
    # Determine trend
    if len(daily_amounts) >= 14:
        first_half = statistics.mean(daily_amounts[:7])
        second_half = statistics.mean(daily_amounts[7:])
        trend = "increasing" if second_half > first_half else "decreasing"
        predictions["trend"] = {
            "direction": trend,
            "strength": abs(second_half - first_half) / first_half * 100
        }
    
    return predictions

async def get_category_breakdown(user_id: str, start_date: datetime, end_date: datetime) -> Dict:
    """Get detailed breakdown of spending by category."""
    db = await get_database()
    
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"user_id": user_id},
                    {"shared_expenses.user_id": user_id}
                ],
                "date": {"$gte": start_date, "$lte": end_date}
            }
        },
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.category",
                "total": {"$sum": "$items.price"},
                "count": {"$sum": 1},
                "items": {"$push": "$items.name"},
                "dates": {"$push": "$date"}
            }
        },
        {"$sort": {"total": -1}}
    ]
    
    results = await db.receipts.aggregate(pipeline).to_list(length=None)
    
    # Process results
    category_breakdown = {}
    for result in results:
        category = result["_id"]
        category_breakdown[category] = {
            "total": result["total"],
            "count": result["count"],
            "items": result["items"],
            "dates": result["dates"],
            "average": result["total"] / result["count"] if result["count"] > 0 else 0
        }
    
    return category_breakdown