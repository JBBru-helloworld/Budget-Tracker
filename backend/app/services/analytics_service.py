# app/services/analytics_service.py
from datetime import datetime, timedelta
from app.database import get_database

async def get_spending_summary(user_id, start_date, end_date, category=None):
    """Get spending summary for a specific date range."""
    db = get_database()
    
    # Build pipeline for aggregation
    match_stage = {
        "user_id": user_id,
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
            "total": {"$sum": "$items.price"}
        }},
        {"$sort": {"_id": 1}}
    ])
    
    # Execute aggregation
    results = await db.receipts.aggregate(pipeline).to_list(length=None)
    
    # Format results
    spending_data = []
    
    if days_diff <= 31:
        # Fill in any missing dates for daily views
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime(group_format)
            found = False
            
            for item in results:
                if item["_id"] == date_str:
                    spending_data.append({
                        "date": date_str,
                        "amount": item["total"]
                    })
                    found = True
                    break
            
            if not found:
                spending_data.append({
                    "date": date_str,
                    "amount": 0
                })
            
            current_date += timedelta(days=1)
    else:
        # For yearly view, just use the aggregated results
        for item in results:
            spending_data.append({
                "date": item["_id"],
                "amount": item["total"]
            })
    
    return spending_data