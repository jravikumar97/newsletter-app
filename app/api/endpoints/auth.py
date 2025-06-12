from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import UserLogin, Token, ChangePassword
from app.schemas.user import UserResponse
from app.core.auth import authenticate_user, create_access_token, get_current_user, get_current_active_user
from app.core.config import settings
from app.crud import user as user_crud

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    """
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Update login tracking
    user.login_count = (user.login_count or 0) + 1
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    user.last_active_at = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
        "user_id": user.id,
        "email": user.email
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user = Depends(get_current_active_user)):
    """
    Get current authenticated user's profile
    """
    return current_user

@router.post("/logout")
async def logout(current_user = Depends(get_current_active_user)):
    """
    Logout current user (client-side token removal)
    """
    # In a more sophisticated implementation, you might:
    # 1. Add token to a blacklist
    # 2. Update last_active_at
    # 3. Clear refresh tokens
    
    return {"message": "Successfully logged out"}

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    from app.core.auth import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/refresh")
async def refresh_token(current_user = Depends(get_current_user)):
    """
    Refresh access token
    """
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/verify-token")
async def verify_token(current_user = Depends(get_current_active_user)):
    """
    Verify if the current token is valid
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active
    }