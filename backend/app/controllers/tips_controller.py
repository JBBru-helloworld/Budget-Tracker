# app/controllers/tips_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.tip_model import TipResponse
from app.services.tip_service import get_general_tips, get_personalized_tips
from app.controllers.auth_controller import verify_token

router = APIRouter()

@router.get("/", response_model=List[TipResponse])
async def get_tips(
    user_id: str = Depends(verify_token),
    category: Optional[str] = None,
    personalized: bool = False,
    limit: int = 5
):

    # Get money-saving tips, either general or personalized based on spending patterns
    try:
        if personalized:
            # Get personalized tips based on user's spending patterns
            tips = await get_personalized_tips(user_id["uid"], category, limit)
        else:
            # Get general money-saving tips
            tips = await get_general_tips(category, limit)
        
        return tips
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tips: {str(e)}"
        )