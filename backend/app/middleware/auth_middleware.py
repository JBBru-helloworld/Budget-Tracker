# backend/app/middleware/auth_middleware.py
from fastapi import Request, HTTPException, status
from ..services.firebase_service import verify_firebase_token
import re

# Routes that don't require authentication
PUBLIC_ROUTES = [
    r"^/$",                  # Root endpoint
    r"^/api/auth/register$", # Registration endpoint
    r"^/docs",               # Swagger docs
    r"^/redoc",              # Redoc docs
    r"^/openapi.json",       # OpenAPI schema
]

async def auth_middleware(request: Request, call_next):

    # Middleware to handle authentication for protected routes

    # Check if the route is public
    path = request.url.path
    if any(re.match(pattern, path) for pattern in PUBLIC_ROUTES):
        return await call_next(request)
    
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )
    
    # Extract and verify token
    token = auth_header.split(" ")[1]
    try:
        user_id = await verify_firebase_token(token)
        # Add user_id to request state
        request.state.user_id = user_id
    except HTTPException as e:
        # Re-raise the exception from verify_firebase_token
        raise e
    
    return await call_next(request)