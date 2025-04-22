from fastapi import APIRouter
from ..controllers import user_profile_controller, category_controller

router = APIRouter()
router.include_router(user_profile_controller.router, prefix="/profiles", tags=["profiles"])
router.include_router(category_controller.router, prefix="/categories", tags=["categories"])