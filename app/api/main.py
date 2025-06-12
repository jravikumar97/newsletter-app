from fastapi import APIRouter
from app.api.endpoints import users, auth, interests, email

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(interests.router, prefix="/interests", tags=["interests"])
api_router.include_router(email.router, prefix="/email", tags=["email"])

# Add basic API info endpoint
@api_router.get("/")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Newsletter Curator API v1.0",
        "endpoints": {
            "users": "/api/v1/users",
            "auth": "/api/v1/auth",
            "interests": "/api/v1/interests",
            "email": "/api/v1/email",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "User Management",
            "JWT Authentication", 
            "Interest Management",
            "User Preferences",
            "Gmail Integration",
            "Newsletter Detection",
            "Email Synchronization"
        ]
    }