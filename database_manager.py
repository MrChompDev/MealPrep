import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mealprep.db"

class DatabaseManager:
    """Centralized database operations manager"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    # User operations
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, name, password_hash, two_factor, profile_pic, created_at
            FROM users WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'password_hash': user[3],
                'two_factor': bool(user[4]),
                'profile_pic': user[5],
                'created_at': user[6]
            }
        return None
    
    def create_user(self, email: str, name: str, password_hash: Optional[str] = None) -> int:
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (email, name, password_hash)
            VALUES (?, ?, ?)
        ''', (email, name, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id
    
    def update_user(self, email: str, **kwargs):
        """Update user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clauses = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['name', 'password_hash', 'two_factor', 'profile_pic']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if set_clauses:
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE email = ?"
            params.append(email)
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    # Meal operations
    def get_all_meals(self) -> List[Dict]:
        """Get all meals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, price, calories, category, 
                   subscription, removable_ingredients, allergens, week, image
            FROM meals
            ORDER BY name
        ''')
        
        meals = []
        for row in cursor.fetchall():
            meals.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3],
                'calories': row[4],
                'category': row[5],
                'subscription': bool(row[6]),
                'removable_ingredients': json.loads(row[7]) if row[7] else [],
                'allergens': json.loads(row[8]) if row[8] else [],
                'week': row[9],
                'image': row[10]
            })
        
        conn.close()
        return meals
    
    def get_meal_by_id(self, meal_id: int) -> Optional[Dict]:
        """Get meal by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, price, calories, category, 
                   subscription, removable_ingredients, allergens, week, image
            FROM meals WHERE id = ?
        ''', (meal_id,))
        
        meal = cursor.fetchone()
        conn.close()
        
        if meal:
            return {
                'id': meal[0],
                'name': meal[1],
                'description': meal[2],
                'price': meal[3],
                'calories': meal[4],
                'category': meal[5],
                'subscription': bool(meal[6]),
                'removable_ingredients': json.loads(meal[7]) if meal[7] else [],
                'allergens': json.loads(meal[8]) if meal[8] else [],
                'week': meal[9],
                'image': meal[10]
            }
        return None
    
    def create_meal(self, meal_data: Dict) -> int:
        """Create new meal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO meals 
            (id, name, description, price, calories, category, subscription,
             removable_ingredients, allergens, week, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            meal_data['id'],
            meal_data['name'],
            meal_data.get('description', ''),
            meal_data['price'],
            meal_data.get('calories', 0),
            meal_data.get('category', ''),
            meal_data.get('subscription', False),
            json.dumps(meal_data.get('removable_ingredients', [])),
            json.dumps(meal_data.get('allergens', [])),
            meal_data.get('week', 0),
            meal_data.get('image', '')
        ))
        
        meal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return meal_id
    
    def update_meal(self, meal_id: int, meal_data: Dict):
        """Update meal information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clauses = []
        params = []
        
        for key, value in meal_data.items():
            if key in ['name', 'description', 'price', 'calories', 'category', 'subscription', 'week', 'image']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
            elif key in ['removable_ingredients', 'allergens']:
                set_clauses.append(f"{key} = ?")
                params.append(json.dumps(value))
        
        if set_clauses:
            query = f"UPDATE meals SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(meal_id)
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def delete_meal(self, meal_id: int):
        """Delete meal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
        conn.commit()
        conn.close()
    
    # Order operations
    def create_order(self, order_data: Dict) -> str:
        """Create new order"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user ID
        user_email = order_data['user']['email']
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        user_result = cursor.fetchone()
        user_id = user_result[0] if user_result else None
        
        # Insert order
        cursor.execute('''
            INSERT INTO orders 
            (order_id, user_id, status, driver, eta, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            order_data['order_id'],
            user_id,
            order_data.get('status', 'Preparing'),
            order_data.get('driver', 'John'),
            order_data.get('eta', datetime.now().strftime("%H:%M")),
            order_data.get('source', 'one_off')
        ))
        
        order_db_id = cursor.lastrowid
        
        # Insert order items
        for meal_item in order_data['meals']:
            if isinstance(meal_item, dict):
                meal_id = meal_item.get('id')
                quantity = meal_item.get('quantity', 1)
            else:
                meal_id = meal_item
                quantity = 1
            
            # Get meal price
            cursor.execute("SELECT price FROM meals WHERE id = ?", (meal_id,))
            meal_result = cursor.fetchone()
            unit_price = int(meal_result[0] * 100) if meal_result else 0
            
            cursor.execute('''
                INSERT INTO order_items 
                (order_id, meal_id, quantity, unit_price_cents)
                VALUES (?, ?, ?, ?)
            ''', (order_db_id, meal_id, quantity, unit_price))
        
        conn.commit()
        conn.close()
        
        return order_data['order_id']
    
    def get_user_orders(self, user_email: str) -> List[Dict]:
        """Get all orders for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.order_id, o.status, o.driver, o.eta, o.created_at,
                   oi.meal_id, oi.quantity, oi.unit_price_cents,
                   m.name, m.price as meal_price
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN meals m ON oi.meal_id = m.id
            WHERE u.email = ?
            ORDER BY o.created_at DESC
        ''', (user_email,))
        
        orders_dict = {}
        for row in cursor.fetchall():
            order_id = row[0]
            
            if order_id not in orders_dict:
                orders_dict[order_id] = {
                    'order_id': order_id,
                    'status': row[1],
                    'driver': row[2],
                    'eta': row[3],
                    'created_at': row[4],
                    'meals': [],
                    'total_price': 0
                }
            
            if row[5]:  # meal_id exists
                orders_dict[order_id]['meals'].append({
                    'id': row[5],
                    'quantity': row[6],
                    'unit_price_cents': row[7],
                    'name': row[8],
                    'price': row[9]
                })
                orders_dict[order_id]['total_price'] += row[6] * row[9]
        
        conn.close()
        return list(orders_dict.values())
    
    # Chat operations
    def log_chat_message(self, user_email: str, message: str, response: str):
        """Log chat message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        user_result = cursor.fetchone()
        user_id = user_result[0] if user_result else None
        
        cursor.execute('''
            INSERT INTO chat_logs 
            (user_id, message, response)
            VALUES (?, ?, ?)
        ''', (user_id, message, response))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, user_email: str, limit: int = 50) -> List[Dict]:
        """Get chat history for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cl.message, cl.response, cl.created_at
            FROM chat_logs cl
            JOIN users u ON cl.user_id = u.id
            WHERE u.email = ?
            ORDER BY cl.created_at DESC
            LIMIT ?
        ''', (user_email, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'message': row[0],
                'response': row[1],
                'created_at': row[2]
            })
        
        conn.close()
        return history
    
    # Configuration operations
    def get_chat_config(self) -> Dict:
        """Get chat configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT supported_meal, trigger_word, success_response, 
                   fallback_response, unknown_response
            FROM chat_config 
            WHERE id = 1
        ''')
        
        config = cursor.fetchone()
        conn.close()
        
        if config:
            return {
                'supported_meal': config[0],
                'trigger_word': config[1],
                'success_response': config[2],
                'fallback_response': config[3],
                'unknown_response': config[4]
            }
        
        return {
            'supported_meal': 'avocado toast',
            'trigger_word': 'order',
            'success_response': 'Order placed successfully!',
            'fallback_response': 'I can help you with ordering.',
            'unknown_response': 'I didn\'t understand that.'
        }
    
    def update_chat_config(self, config_data: Dict):
        """Update chat configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chat_config 
            SET supported_meal = ?, trigger_word = ?, 
                success_response = ?, fallback_response = ?, unknown_response = ?
            WHERE id = 1
        ''', (
            config_data.get('supported_meal'),
            config_data.get('trigger_word'),
            config_data.get('success_response'),
            config_data.get('fallback_response'),
            config_data.get('unknown_response')
        ))
        
        conn.commit()
        conn.close()
    
    # Analytics operations
    def get_popular_meals(self, limit: int = 10) -> List[Dict]:
        """Get most popular meals based on orders"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.id, m.name, m.price, m.category, COUNT(oi.meal_id) as order_count
            FROM meals m
            LEFT JOIN order_items oi ON m.id = oi.meal_id
            GROUP BY m.id, m.name, m.price, m.category
            ORDER BY order_count DESC
            LIMIT ?
        ''', (limit,))
        
        popular_meals = []
        for row in cursor.fetchall():
            popular_meals.append({
                'id': row[0],
                'name': row[1],
                'price': row[2],
                'category': row[3],
                'order_count': row[4]
            })
        
        conn.close()
        return popular_meals
    
    def get_user_statistics(self, user_email: str) -> Dict:
        """Get statistics for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Order count
        cursor.execute('''
            SELECT COUNT(DISTINCT o.id)
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE u.email = ?
        ''', (user_email,))
        order_count = cursor.fetchone()[0]
        
        # Total spent
        cursor.execute('''
            SELECT SUM(oi.quantity * oi.unit_price_cents) / 100.0
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN order_items oi ON o.id = oi.order_id
            WHERE u.email = ?
        ''', (user_email,))
        total_spent = cursor.fetchone()[0] or 0
        
        # Favorite categories
        cursor.execute('''
            SELECT m.category, COUNT(*) as count
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN meals m ON oi.meal_id = m.id
            WHERE u.email = ?
            GROUP BY m.category
            ORDER BY count DESC
            LIMIT 3
        ''', (user_email,))
        favorite_categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'order_count': order_count,
            'total_spent': total_spent,
            'favorite_categories': favorite_categories
        }
    
    # Developer operations
    def get_chat_logs(self, limit: int = 100) -> List[Dict]:
        """Get all chat logs for developer dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_email, user_message, bot_response, timestamp, intent, confidence
            FROM chat_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'user_email': row[0],
                'user_message': row[1],
                'bot_response': row[2],
                'timestamp': row[3],
                'intent': row[4],
                'confidence': row[5]
            })
        
        conn.close()
        return logs
    
    def get_system_logs(self, limit: int = 50) -> List[Dict]:
        """Get system logs for developer dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, level, message, source
            FROM logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'level': row[1],
                'message': row[2],
                'source': row[3]
            })
        
        conn.close()
        return logs
    
    def get_all_users(self) -> List[Dict]:
        """Get all users for developer dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, name, created_at
            FROM users 
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return users
    
    def get_all_orders(self) -> List[Dict]:
        """Get all orders for developer dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT order_id, user_email, total, status, created_at
            FROM orders 
            ORDER BY created_at DESC
        ''')
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'order_id': row[0],
                'user_email': row[1],
                'total': row[2],
                'status': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return orders
    
    def get_chat_logs_by_date(self, date) -> List[Dict]:
        """Get chat logs for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM chat_logs 
            WHERE DATE(timestamp) = DATE(?)
        ''', (date,))
        
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
