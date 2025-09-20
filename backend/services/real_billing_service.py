import requests
import os
import sqlite3
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

class RealBillingService:
    def __init__(self):
        self.flexprice_api_key = os.getenv("FLEXPRICE_API_KEY")
        self.flexprice_base_url = os.getenv("FLEXPRICE_BASE_URL", "https://api.flexprice.com")
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
                email TEXT,
                credits INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
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
                flexprice_transaction_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
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
                flexprice_response TEXT,
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
    
    async def deduct_credits(self, user_id: str, amount: int, action: str = "research_query", details: str = ""):
        """Deduct credits from user account and log transaction"""
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
            (user_id, action, amount, details or f"Deducted {amount} credits for {action}")
        )
        
        conn.commit()
        conn.close()
        
        # If credits are low, trigger Flexprice billing
        if new_credits < 3:
            await self._trigger_low_credits_alert(user_id, new_credits)
    
    async def purchase_credits(self, user_id: str, amount: int, payment_method: str = "card") -> Dict[str, Any]:
        """Purchase credits using Flexprice"""
        try:
            if not self.flexprice_api_key:
                # Fallback: add credits without payment processing
                await self.add_credits(user_id, amount, "manual_purchase")
                return {
                    "success": True,
                    "message": "Credits added (payment processing not configured)",
                    "credits_added": amount
                }
            
            # Create Flexprice transaction
            flexprice_response = await self._create_flexprice_transaction(
                user_id, amount, payment_method
            )
            
            if flexprice_response.get("success"):
                # Add credits to user account
                await self.add_credits(user_id, amount, "credit_purchase", flexprice_response.get("transaction_id"))
                
                return {
                    "success": True,
                    "message": "Credits purchased successfully",
                    "credits_added": amount,
                    "transaction_id": flexprice_response.get("transaction_id")
                }
            else:
                return {
                    "success": False,
                    "message": flexprice_response.get("error", "Payment failed")
                }
                
        except Exception as e:
            print(f"Error purchasing credits: {e}")
            return {
                "success": False,
                "message": f"Payment error: {str(e)}"
            }
    
    async def _create_flexprice_transaction(self, user_id: str, amount: int, payment_method: str) -> Dict[str, Any]:
        """Create a transaction with Flexprice"""
        try:
            url = f"{self.flexprice_base_url}/v1/transactions"
            headers = {
                "Authorization": f"Bearer {self.flexprice_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "user_id": user_id,
                "amount": amount * 0.1,  # $0.10 per credit
                "currency": "USD",
                "description": f"Purchase {amount} research credits",
                "payment_method": payment_method,
                "metadata": {
                    "credits": amount,
                    "service": "smart_research_assistant"
                }
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Store transaction in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO billing_transactions 
                (user_id, transaction_id, amount, currency, status, payment_method, flexprice_response)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get("transaction_id"),
                payload["amount"],
                payload["currency"],
                data.get("status", "pending"),
                payment_method,
                json.dumps(data)
            ))
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "transaction_id": data.get("transaction_id"),
                "status": data.get("status")
            }
            
        except Exception as e:
            print(f"Error creating Flexprice transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_credits(self, user_id: str, amount: int, reason: str = "purchase", transaction_id: str = None):
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
            'INSERT INTO usage_logs (user_id, action, credits_used, details, flexprice_transaction_id) VALUES (?, ?, ?, ?, ?)',
            (user_id, "credit_purchase", -amount, f"Added {amount} credits: {reason}", transaction_id)
        )
        
        conn.commit()
        conn.close()
    
    async def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('SELECT credits, email, created_at, last_updated FROM users WHERE user_id = ?', (user_id,))
        user_result = cursor.fetchone()
        
        if user_result is None:
            # Create new user
            cursor.execute('INSERT INTO users (user_id, credits) VALUES (?, ?)', (user_id, 10))
            conn.commit()
            user_result = (10, None, datetime.now().isoformat(), datetime.now().isoformat())
        
        credits, email, created_at, last_updated = user_result
        
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
            SELECT action, credits_used, timestamp, details, flexprice_transaction_id
            FROM usage_logs 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (user_id,))
        
        recent_activity = cursor.fetchall()
        
        # Get billing history
        cursor.execute('''
            SELECT transaction_id, amount, currency, status, timestamp
            FROM billing_transactions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''', (user_id,))
        
        billing_history = cursor.fetchall()
        
        conn.close()
        
        return {
            "user_id": user_id,
            "email": email,
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
                    "details": details,
                    "transaction_id": transaction_id
                }
                for action, credits_used, timestamp, details, transaction_id in recent_activity
            ],
            "billing_history": [
                {
                    "transaction_id": transaction_id,
                    "amount": amount,
                    "currency": currency,
                    "status": status,
                    "timestamp": timestamp
                }
                for transaction_id, amount, currency, status, timestamp in billing_history
            ]
        }
    
    async def _trigger_low_credits_alert(self, user_id: str, current_credits: int):
        """Trigger alert when credits are low"""
        print(f"ALERT: User {user_id} has only {current_credits} credits remaining")
        # Here you could send email notifications, push notifications, etc.
    
    async def get_billing_summary(self, user_id: str) -> Dict[str, Any]:
        """Get billing summary for dashboard"""
        stats = await self.get_usage_stats(user_id)
        
        return {
            "current_credits": stats["current_credits"],
            "reports_generated": stats["total_reports_generated"],
            "credits_used_today": await self._get_credits_used_today(user_id),
            "credits_used_this_month": await self._get_credits_used_this_month(user_id),
            "estimated_remaining_queries": stats["current_credits"],
            "billing_enabled": bool(self.flexprice_api_key)
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

