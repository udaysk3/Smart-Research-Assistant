from typing import Dict, Any
from datetime import datetime, timedelta
import sqlite3
import os

class BillingService:
    def __init__(self):
        self.db_path = "billing.db"
        self.init_database()
    
    def init_database(self):
        """Initialize the billing database"""
        conn = sqlite3.connect(self.db_path)
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
        
        # Create usage_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                credits_used INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def check_credits(self, user_id: str) -> bool:
        """Check if user has sufficient credits"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT credits FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result is None:
            # Create new user with default credits
            cursor.execute('INSERT INTO users (user_id, credits) VALUES (?, ?)', (user_id, 10))
            conn.commit()
            credits = 10
        else:
            credits = result[0]
        
        conn.close()
        return credits > 0
    
    async def deduct_credits(self, user_id: str, amount: int, action: str = "research_query"):
        """Deduct credits from user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current credits
        cursor.execute('SELECT credits FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result is None:
            # Create new user
            cursor.execute('INSERT INTO users (user_id, credits) VALUES (?, ?)', (user_id, 10))
            current_credits = 10
        else:
            current_credits = result[0]
        
        # Deduct credits
        new_credits = max(0, current_credits - amount)
        cursor.execute(
            'UPDATE users SET credits = ?, last_updated = CURRENT_TIMESTAMP WHERE user_id = ?',
            (new_credits, user_id)
        )
        
        # Log usage
        cursor.execute(
            'INSERT INTO usage_logs (user_id, action, credits_used, details) VALUES (?, ?, ?, ?)',
            (user_id, action, amount, f"Deducted {amount} credits for {action}")
        )
        
        conn.commit()
        conn.close()
    
    async def add_credits(self, user_id: str, amount: int, reason: str = "purchase"):
        """Add credits to user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current credits
        cursor.execute('SELECT credits FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result is None:
            # Create new user
            cursor.execute('INSERT INTO users (user_id, credits) VALUES (?, ?)', (user_id, amount))
            current_credits = 0
        else:
            current_credits = result[0]
        
        # Add credits
        new_credits = current_credits + amount
        cursor.execute(
            'UPDATE users SET credits = ?, last_updated = CURRENT_TIMESTAMP WHERE user_id = ?',
            (new_credits, user_id)
        )
        
        # Log usage
        cursor.execute(
            'INSERT INTO usage_logs (user_id, action, credits_used, details) VALUES (?, ?, ?, ?)',
            (user_id, "credit_purchase", -amount, f"Added {amount} credits: {reason}")
        )
        
        conn.commit()
        conn.close()
    
    async def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('SELECT credits, created_at, last_updated FROM users WHERE user_id = ?', (user_id,))
        user_result = cursor.fetchone()
        
        if user_result is None:
            # Create new user
            cursor.execute('INSERT INTO users (user_id, credits) VALUES (?, ?)', (user_id, 10))
            conn.commit()
            user_result = (10, datetime.now().isoformat(), datetime.now().isoformat())
        
        credits, created_at, last_updated = user_result
        
        # Get usage logs
        cursor.execute('''
            SELECT action, COUNT(*) as count, SUM(credits_used) as total_credits
            FROM usage_logs 
            WHERE user_id = ? AND action != 'credit_purchase'
            GROUP BY action
        ''', (user_id,))
        
        usage_breakdown = cursor.fetchall()
        
        # Get total reports generated
        cursor.execute('''
            SELECT COUNT(*) FROM usage_logs 
            WHERE user_id = ? AND action = 'research_query'
        ''', (user_id,))
        
        total_reports = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute('''
            SELECT action, credits_used, timestamp, details
            FROM usage_logs 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (user_id,))
        
        recent_activity = cursor.fetchall()
        
        conn.close()
        
        return {
            "user_id": user_id,
            "current_credits": credits,
            "total_reports_generated": total_reports,
            "account_created": created_at,
            "last_activity": last_updated,
            "usage_breakdown": [
                {"action": action, "count": count, "total_credits": total_credits}
                for action, count, total_credits in usage_breakdown
            ],
            "recent_activity": [
                {
                    "action": action,
                    "credits_used": credits_used,
                    "timestamp": timestamp,
                    "details": details
                }
                for action, credits_used, timestamp, details in recent_activity
            ]
        }
    
    async def get_billing_summary(self, user_id: str) -> Dict[str, Any]:
        """Get billing summary for dashboard"""
        stats = await self.get_usage_stats(user_id)
        
        return {
            "current_credits": stats["current_credits"],
            "reports_generated": stats["total_reports_generated"],
            "credits_used_today": await self._get_credits_used_today(user_id),
            "credits_used_this_month": await self._get_credits_used_this_month(user_id),
            "estimated_remaining_queries": stats["current_credits"]
        }
    
    async def _get_credits_used_today(self, user_id: str) -> int:
        """Get credits used today"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('''
            SELECT SUM(credits_used) FROM usage_logs 
            WHERE user_id = ? AND DATE(timestamp) = ? AND action != 'credit_purchase'
        ''', (user_id, today))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result or 0
    
    async def _get_credits_used_this_month(self, user_id: str) -> int:
        """Get credits used this month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get first day of current month
        first_day = datetime.now().replace(day=1).date()
        cursor.execute('''
            SELECT SUM(credits_used) FROM usage_logs 
            WHERE user_id = ? AND DATE(timestamp) >= ? AND action != 'credit_purchase'
        ''', (user_id, first_day))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result or 0


