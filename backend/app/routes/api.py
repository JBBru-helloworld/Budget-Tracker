# app/routes/api.py
from fastapi import APIRouter
from app.controllers import (
    auth_controller,
    category_controller,
    receipt_controller,
    profile_controller,
    analytics_controller,
    tips_controller,
    settings_controller,
    scan_controller
)

# Create main API router
api_router = APIRouter()

# Register all controllers
api_router.include_router(
    auth_controller.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    profile_controller.router,
    prefix="/profile",
    tags=["User Profile"]
)

api_router.include_router(
    receipt_controller.router,
    prefix="/receipts",
    tags=["Receipts"]
)

api_router.include_router(
    scan_controller.router,
    prefix="/scan",
    tags=["Receipt Scanning"]
)

api_router.include_router(
    category_controller.router,
    prefix="/categories",
    tags=["Categories"]
)

api_router.include_router(
    analytics_controller.router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    tips_controller.router,
    prefix="/tips",
    tags=["Money-Saving Tips"]
)

api_router.include_router(
    settings_controller.router,
    prefix="/settings",
    tags=["User Settings"]
)