from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import hashlib
import secrets

# Database configuration
# Get the directory where this file is located (backend directory)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BACKEND_DIR, "research_assistant.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    salt = Column(String)
    credits = Column(Integer, default=10)  # Starting credits
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    def set_password(self, password: str):
        """Set password with salt and hash"""
        self.salt = secrets.token_hex(16)
        self.password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), self.salt.encode('utf-8'), 100000).hex()
    
    def check_password(self, password: str) -> bool:
        """Check if password is correct"""
        if not self.salt or not self.password_hash:
            return False
        hash_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), self.salt.encode('utf-8'), 100000).hex()
        return hash_check == self.password_hash

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    question = Column(Text)
    answer = Column(Text)
    citations = Column(Text)  # JSON string
    sources = Column(Text)    # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    filename = Column(String)
    file_path = Column(String)
    file_type = Column(String)
    total_pages = Column(Integer)
    total_words = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    action = Column(String)
    credits_used = Column(Integer)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

