from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from typing import List, Dict, Any
from datetime import datetime
import json

# Create admin app
admin_app = FastAPI(title="Smart Research Assistant Admin", version="1.0.0")

# Templates
templates = Jinja2Templates(directory="templates")

def init_admin_database():
    """Initialize the admin database with migration support"""
    conn = sqlite3.connect("billing.db")
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            credits INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add email column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add is_active column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create usage_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            credits_used INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')
    
    # Add flexprice_transaction_id column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE usage_logs ADD COLUMN flexprice_transaction_id TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create billing_transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            transaction_id TEXT UNIQUE,
            amount REAL,
            currency TEXT DEFAULT 'USD',
            status TEXT,
            payment_method TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            flexprice_response TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_admin_database()

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect("billing.db")

@admin_app.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user statistics
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM usage_logs WHERE action = 'research_query'")
    total_reports = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(credits_used) FROM usage_logs WHERE action != 'credit_purchase'")
    total_credits_used = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM billing_transactions WHERE status = 'completed'")
    total_transactions = cursor.fetchone()[0]
    
    # Get recent users (handle missing email column gracefully)
    try:
        cursor.execute("""
            SELECT user_id, email, credits, created_at, last_updated 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_users = cursor.fetchall()
    except sqlite3.OperationalError:
        # Fallback if email column doesn't exist
        cursor.execute("""
            SELECT user_id, NULL as email, credits, created_at, last_updated 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_users = cursor.fetchall()
    
    # Get recent activity
    cursor.execute("""
        SELECT ul.user_id, ul.action, ul.credits_used, ul.timestamp, ul.details
        FROM usage_logs ul
        ORDER BY ul.timestamp DESC 
        LIMIT 20
    """)
    recent_activity = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "total_users": total_users,
        "total_reports": total_reports,
        "total_credits_used": total_credits_used,
        "total_transactions": total_transactions,
        "recent_users": recent_users,
        "recent_activity": recent_activity
    })

@admin_app.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, page: int = 1, limit: int = 50):
    """List all users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    offset = (page - 1) * limit
    
    try:
        cursor.execute("""
            SELECT user_id, email, credits, created_at, last_updated, is_active
            FROM users 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        users = cursor.fetchall()
    except sqlite3.OperationalError:
        # Fallback if columns don't exist
        cursor.execute("""
            SELECT user_id, NULL as email, credits, created_at, last_updated, 1 as is_active
            FROM users 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        users = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    conn.close()
    
    return templates.TemplateResponse("users_list.html", {
        "request": request,
        "users": users,
        "page": page,
        "limit": limit,
        "total_users": total_users,
        "total_pages": (total_users + limit - 1) // limit
    })

@admin_app.get("/users/{user_id}", response_class=HTMLResponse)
async def user_detail(request: Request, user_id: str):
    """User detail page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's usage logs
    cursor.execute("""
        SELECT action, credits_used, timestamp, details, flexprice_transaction_id
        FROM usage_logs 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, (user_id,))
    
    usage_logs = cursor.fetchall()
    
    # Get user's billing transactions
    cursor.execute("""
        SELECT transaction_id, amount, currency, status, timestamp, flexprice_response
        FROM billing_transactions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, (user_id,))
    
    billing_transactions = cursor.fetchall()
    
    # Get usage statistics
    cursor.execute("""
        SELECT action, COUNT(*) as count, SUM(credits_used) as total_credits
        FROM usage_logs 
        WHERE user_id = ? AND action != 'credit_purchase'
        GROUP BY action
    """, (user_id,))
    
    usage_stats = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("user_detail.html", {
        "request": request,
        "user": user,
        "usage_logs": usage_logs,
        "billing_transactions": billing_transactions,
        "usage_stats": usage_stats
    })

@admin_app.get("/transactions", response_class=HTMLResponse)
async def transactions_list(request: Request, page: int = 1, limit: int = 50):
    """List all billing transactions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    offset = (page - 1) * limit
    
    cursor.execute("""
        SELECT bt.*, u.email
        FROM billing_transactions bt
        LEFT JOIN users u ON bt.user_id = u.user_id
        ORDER BY bt.timestamp DESC 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    transactions = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM billing_transactions")
    total_transactions = cursor.fetchone()[0]
    
    conn.close()
    
    return templates.TemplateResponse("transactions_list.html", {
        "request": request,
        "transactions": transactions,
        "page": page,
        "limit": limit,
        "total_transactions": total_transactions,
        "total_pages": (total_transactions + limit - 1) // limit
    })

@admin_app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    """Analytics dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Daily usage for last 30 days
    cursor.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as reports, SUM(credits_used) as credits
        FROM usage_logs 
        WHERE action = 'research_query' AND timestamp >= datetime('now', '-30 days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """)
    
    daily_usage = cursor.fetchall()
    
    # User growth
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as new_users
        FROM users 
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
    """)
    
    user_growth = cursor.fetchall()
    
    # Top users by usage
    cursor.execute("""
        SELECT u.user_id, u.email, COUNT(ul.id) as reports, SUM(ul.credits_used) as credits_used
        FROM users u
        LEFT JOIN usage_logs ul ON u.user_id = ul.user_id AND ul.action = 'research_query'
        GROUP BY u.user_id, u.email
        ORDER BY reports DESC
        LIMIT 10
    """)
    
    top_users = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "daily_usage": daily_usage,
        "user_growth": user_growth,
        "top_users": top_users
    })

@admin_app.post("/api/users/{user_id}/credits")
async def add_user_credits(user_id: str, amount: int):
    """Add credits to a user (admin action)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_credits = result[0]
    new_credits = current_credits + amount
    
    # Update user credits
    cursor.execute(
        "UPDATE users SET credits = ?, last_updated = CURRENT_TIMESTAMP WHERE user_id = ?",
        (new_credits, user_id)
    )
    
    # Log the action
    cursor.execute(
        "INSERT INTO usage_logs (user_id, action, credits_used, details) VALUES (?, ?, ?, ?)",
        (user_id, "admin_credit_adjustment", -amount, f"Admin added {amount} credits")
    )
    
    conn.commit()
    conn.close()
    
    return {"message": f"Added {amount} credits to user {user_id}", "new_balance": new_credits}

@admin_app.delete("/api/users/{user_id}")
async def deactivate_user(user_id: str):
    """Deactivate a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE users SET is_active = 0, last_updated = CURRENT_TIMESTAMP WHERE user_id = ?",
        (user_id,)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": f"User {user_id} deactivated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(admin_app, host="0.0.0.0", port=8001)
