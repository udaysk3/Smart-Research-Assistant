"""
Authentication Service for Smart Research Assistant
"""
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models.database import User, UserSession, get_db
import os

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.token_expiry_hours = 24
    
    def generate_token(self) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    def create_user(self, db: Session, username: str, email: str, password: str) -> Dict[str, Any]:
        """Create a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                raise ValueError("Email already registered")
            if existing_user.username == username:
                raise ValueError("Username already taken")
        
        # Create new user
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            credits=10  # Starting credits
        )
        user.set_password(password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "credits": user.credits,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    
    def authenticate_user(self, db: Session, username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        user = db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return None
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "credits": user.credits,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    
    def create_session(self, db: Session, user_id: str) -> str:
        """Create a new user session"""
        # Deactivate old sessions
        db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({"is_active": False})
        
        # Create new session
        token = self.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        
        session = UserSession(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(session)
        db.commit()
        
        return token
    
    def validate_token(self, db: Session, token: str) -> Optional[Dict[str, Any]]:
        """Validate token and return user data"""
        print(f"🔍 Validating token in auth service: {token[:20]}...")
        
        session = db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            print(f"❌ No valid session found for token: {token[:20]}...")
            return None
        
        print(f"✅ Session found for user_id: {session.user_id}")
        
        user = db.query(User).filter(User.user_id == session.user_id).first()
        if not user or not user.is_active:
            print(f"❌ User not found or inactive: {session.user_id}")
            return None
        
        print(f"✅ User found: {user.username}")
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "credits": user.credits
        }
    
    def logout_user(self, db: Session, token: str) -> bool:
        """Logout user by deactivating session"""
        session = db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        
        return False
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            return None
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "credits": user.credits,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    
    def update_user_credits(self, db: Session, user_id: str, credits_change: int) -> bool:
        """Update user credits"""
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            return False
        
        user.credits += credits_change
        if user.credits < 0:
            user.credits = 0
        
        db.commit()
        return True
    
    def check_user_credits(self, db: Session, user_id: str, required_credits: int = 1) -> bool:
        """Check if user has enough credits"""
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            return False
        
        return user.credits >= required_credits
