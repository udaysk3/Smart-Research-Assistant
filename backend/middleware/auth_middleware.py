"""
Authentication Middleware for FastAPI
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models.database import get_db
from services.auth_service import AuthService
from typing import Optional

security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current authenticated user"""
    token = credentials.credentials
    print(f"🔍 Validating token: {token[:20]}...")
    
    user_data = auth_service.validate_token(db, token)
    if not user_data:
        print(f"❌ Token validation failed for: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ Token validation successful for user: {user_data.get('username')}")
    return user_data

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

def require_auth(func):
    """Decorator to require authentication for endpoints"""
    async def wrapper(*args, **kwargs):
        # This will be handled by the Depends(get_current_user) in the endpoint
        return await func(*args, **kwargs)
    return wrapper
