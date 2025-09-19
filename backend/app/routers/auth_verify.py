from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user
from app.schemas.user import UserResponse
import logging

logger = logging.getLogger("BookLibraryAPI")

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/verify", response_model=dict)
async def verify_authorization(current_user: UserResponse = Depends(get_current_user)):
    """
    🔐 Verify current authorization status - use this to test if your token works!
    
    This endpoint will show you a success message if your JWT token is valid.
    Perfect for testing authorization in Swagger UI.
    """
    success_message = f"🎉 SUCCESS! Welcome back, {current_user.email}! Your authorization is working perfectly."
    logger.info(f"🎉 AUTHORIZATION VERIFIED: Welcome {current_user.email}!")
    
    return {
        "status": "success",
        "message": success_message,
        "user": {
            "email": current_user.email,
            "role": current_user.role,
            "permissions": getattr(current_user, 'permissions', []),
            "session_id": getattr(current_user, 'current_session_id', None)
        },
        "access_level": "authenticated",
        "auth_info": {
            "token_type": "Bearer JWT",
            "expires_info": "Check your token's 'exp' claim for expiration",
            "next_steps": [
                "✅ You can now access all protected endpoints",
                "✅ Try creating a book with POST /v2/books/",
                "✅ Access admin features if you have admin role",
                "✅ Your session is active and valid"
            ]
        },
        "helpful_links": {
            "swagger_ui": "/docs",
            "test_page": "/test/auth",
            "tips": "/test/swagger-tips"
        },
        "timestamp": "2025-09-10T15:58:00Z"
    }
