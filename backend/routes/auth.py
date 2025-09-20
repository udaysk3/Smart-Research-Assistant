"""
Authentication Routes for Smart Research Assistant
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from models.database import get_db
from services.auth_service import AuthService
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])
auth_service = AuthService()

# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    credits: int
    created_at: Optional[str] = None
    last_login: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=AuthResponse)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Validate password strength
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        if len(user_data.username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long"
            )
        
        # Create user
        user = auth_service.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        
        # Create session
        token = auth_service.create_session(db, user["user_id"])
        
        return AuthResponse(
            access_token=token,
            user=UserResponse(**user)
        )
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Registration error: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user"""
    try:
        user = auth_service.authenticate_user(
            db=db,
            username_or_email=login_data.username_or_email,
            password=login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create session
        token = auth_service.create_session(db, user["user_id"])
        
        return AuthResponse(
            access_token=token,
            user=UserResponse(**user)
        )
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Login error: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/logout")
async def logout_user(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user"""
    # Note: In a real implementation, you'd need to pass the token
    # For now, we'll just return success
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(**current_user)

@router.get("/verify-token")
async def verify_token(
    current_user: dict = Depends(get_current_user)
):
    """Verify if token is valid"""
    return {"valid": True, "user": current_user}
