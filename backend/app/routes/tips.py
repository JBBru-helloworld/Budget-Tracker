# backend/app/routes/tips.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.models import SavingTip, Category
from ..services.ai_service import generate_saving_tips
from datetime import datetime
from typing import List

router = APIRouter()
security = HTTPBearer()

@router.get("/")
async def get_saving_tips(
    request: Request,
    category: str = None,
    limit: int = 5,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # Get personalized money-saving tips
    try:
        user_id = request.state.user_id
        
        # Get user's spending data from the last 30 days
        now = datetime.now()
        thirty_days_ago = now - datetime.timedelta(days=30)
        
        # Query database for receipts in the last 30 days
        spending_by_category = {cat.value: 0 for cat in Category}
        cursor = request.app.mongodb["receipts"].find({
            "user_id": user_id,
            "date": {"$gte": thirty_days_ago, "$lte": now}
        })
        
        async for receipt in cursor:
            for item in receipt["items"]:
                cat = item["category"]
                if cat in spending_by_category:
                    item_total = item["price"] * item.get("quantity", 1)
                    spending_by_category[cat] += item_total
        
        # Filter out categories with no spending
        spending_by_category = {k: v for k, v in spending_by_category.items() if v > 0}
        
        # If user has no spending data, return generic tips
        if not spending_by_category:
            tips = await request.app.mongodb["saving_tips"].find(
                {"category": Category.OTHER.value if not category else category}
            ).limit(limit).to_list(length=limit)
            
            # Convert ObjectId to string
            for tip in tips:
                tip["_id"] = str(tip["_id"])
                
            return tips
        
        # Check if we already have personalized tips for this user in database
        existing_tips = await request.app.mongodb["saving_tips"].find({
            "user_id": user_id,
            "created_at": {"$gte": thirty_days_ago}
        }).to_list(length=20)
        
        # If we have enough recent tips, return them
        if len(existing_tips) >= limit:
            # Filter by category if specified
            if category:
                existing_tips = [tip for tip in existing_tips if tip["category"] == category]
                
            # Limit results
            existing_tips = existing_tips[:limit]
            
            # Convert ObjectId to string
            for tip in existing_tips:
                tip["_id"] = str(tip["_id"])
                
            return existing_tips
            
        # Generate new tips based on spending patterns
        ai_tips = await generate_saving_tips(user_id, spending_by_category)
        
        # Save new tips to database
        tip_objects = []
        for tip_data in ai_tips:
            tip = SavingTip(
                user_id=user_id,
                category=tip_data["category"],
                title=tip_data["title"],
                description=tip_data["description"],
                ai_generated=True
            )
            tip_objects.append(tip.dict(by_alias=True))
            
        if tip_objects:
            await request.app.mongodb["saving_tips"].insert_many(tip_objects)
            
        # Combine existing and new tips
        all_tips = existing_tips + ai_tips
        
        # Filter by category if specified
        if category:
            all_tips = [tip for tip in all_tips if tip.get("category", "") == category]
            
        # Limit results
        all_tips = all_tips[:limit]
        
        return all_tips
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating saving tips: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_custom_tip(
    request: Request,
    tip: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # Create a custom money-saving tip
    try:
        user_id = request.state.user_id
        
        # Validate input
        if not all(key in tip for key in ["category", "title", "description"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: category, title, description"
            )
            
        # Convert category to lowercase and validate
        tip["category"] = tip["category"].lower()
        if tip["category"] not in [cat.value for cat in Category]:
            tip["category"] = Category.OTHER.value
            
        # Create tip object
        saving_tip = SavingTip(
            user_id=user_id,
            category=tip["category"],
            title=tip["title"],
            description=tip["description"],
            ai_generated=False
        )
        
        # Save to database
        result = await request.app.mongodb["saving_tips"].insert_one(saving_tip.dict(by_alias=True))
        
        # Get created tip with ID
        created_tip = await request.app.mongodb["saving_tips"].find_one({"_id": result.inserted_id})
        created_tip["_id"] = str(created_tip["_id"])
        
        return created_tip
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating saving tip: {str(e)}"
        )