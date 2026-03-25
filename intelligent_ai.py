import sqlite3
import json
import re
import math
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mealprep.db"

class IntelligentAI:
    """Intelligent AI system that learns from user interactions and provides personalized recommendations"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.initialize_ai_tables()
    
    def initialize_ai_tables(self):
        """Create AI-specific tables for learning and tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User behavior tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                action_type TEXT NOT NULL,
                target_id INTEGER,
                target_type TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        # User preferences learning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                preference_type TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        # AI training data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                input_text TEXT NOT NULL,
                context TEXT,
                response TEXT NOT NULL,
                success_rating INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        # Meal similarity matrix
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meal_similarity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal1_id INTEGER NOT NULL,
                meal2_id INTEGER NOT NULL,
                similarity_score REAL NOT NULL,
                FOREIGN KEY (meal1_id) REFERENCES meals (id),
                FOREIGN KEY (meal2_id) REFERENCES meals (id)
            )
        ''')
        
        # User interaction patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interaction_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def track_user_behavior(self, user_email: str, action_type: str, target_id: Optional[int] = None, 
                          target_type: Optional[str] = None, metadata: Optional[Dict] = None):
        """Track user behavior for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_behaviors 
            (user_email, action_type, target_id, target_type, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_email, action_type, target_id, target_type, json.dumps(metadata or {})))
        
        conn.commit()
        conn.close()
        
        # Update preferences based on behavior
        self._update_user_preferences(user_email, action_type, target_id, target_type)
    
    def _update_user_preferences(self, user_email: str, action_type: str, 
                               target_id: Optional[int], target_type: str):
        """Update user preferences based on their behavior"""
        if target_type != 'meal' or not target_id:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get meal details
        cursor.execute('''
            SELECT category, price, calories, allergens, removable_ingredients 
            FROM meals WHERE id = ?
        ''', (target_id,))
        meal = cursor.fetchone()
        
        if not meal:
            conn.close()
            return
            
        category, price, calories, allergens, ingredients = meal
        
        # Update category preference
        weight = 1.0 if action_type == 'order' else 0.5
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (user_email, preference_type, preference_value, weight, updated_at)
            VALUES (?, 'category', ?, ?, CURRENT_TIMESTAMP)
        ''', (user_email, category, weight))
        
        # Update price range preference
        price_range = self._get_price_range(price)
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (user_email, preference_type, preference_value, weight, updated_at)
            VALUES (?, 'price_range', ?, ?, CURRENT_TIMESTAMP)
        ''', (user_email, price_range, weight))
        
        # Update calorie preference
        calorie_range = self._get_calorie_range(calories)
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (user_email, preference_type, preference_value, weight, updated_at)
            VALUES (?, 'calories', ?, ?, CURRENT_TIMESTAMP)
        ''', (user_email, calorie_range, weight))
        
        conn.commit()
        conn.close()
    
    def _get_price_range(self, price: float) -> str:
        """Categorize price into ranges"""
        if price < 10:
            return "budget"
        elif price < 15:
            return "moderate"
        else:
            return "premium"
    
    def _get_calorie_range(self, calories: int) -> str:
        """Categorize calories into ranges"""
        if calories < 400:
            return "light"
        elif calories < 600:
            return "moderate"
        else:
            return "heavy"
    
    def get_personalized_recommendations(self, user_email: str, limit: int = 5) -> List[Dict]:
        """Get personalized meal recommendations for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user preferences
        cursor.execute('''
            SELECT preference_type, preference_value, weight 
            FROM user_preferences 
            WHERE user_email = ?
        ''', (user_email,))
        preferences = cursor.fetchall()
        
        # Get all meals
        cursor.execute('''
            SELECT id, name, description, price, calories, category, 
                   removable_ingredients, allergens
            FROM meals
        ''')
        meals = cursor.fetchall()
        
        conn.close()
        
        if not meals:
            return []
        
        # Score meals based on preferences
        scored_meals = []
        pref_weights = defaultdict(float)
        
        for pref_type, pref_value, weight in preferences:
            pref_weights[(pref_type, pref_value)] = weight
        
        for meal in meals:
            meal_id, name, description, price, calories, category, ingredients, allergens = meal
            score = 0.0
            
            # Category preference
            score += pref_weights.get(('category', category), 0) * 2.0
            
            # Price preference
            price_range = self._get_price_range(price)
            score += pref_weights.get(('price_range', price_range), 0) * 1.5
            
            # Calorie preference
            calorie_range = self._get_calorie_range(calories)
            score += pref_weights.get(('calories', calorie_range), 0) * 1.0
            
            # Add some variety factor
            score += hash(str(meal_id)) % 100 / 100 * 0.5
            
            scored_meals.append({
                'id': meal_id,
                'name': name,
                'description': description,
                'price': price,
                'calories': calories,
                'category': category,
                'score': score
            })
        
        # Sort by score and return top recommendations
        scored_meals.sort(key=lambda x: x['score'], reverse=True)
        return scored_meals[:limit]
    
    def process_user_message(self, user_email: str, message: str) -> Dict:
        """Process user message and provide intelligent response"""
        # Log the interaction
        self._log_chat_interaction(user_email, message)
        
        # Analyze intent
        intent = self._analyze_intent(message)
        
        # Generate response based on intent
        if intent['type'] == 'order':
            return self._handle_order_intent(user_email, intent)
        elif intent['type'] == 'recommendation':
            return self._handle_recommendation_intent(user_email, intent)
        elif intent['type'] == 'information':
            return self._handle_information_intent(user_email, intent)
        else:
            return self._handle_general_intent(user_email, intent)
    
    def _analyze_intent(self, message: str) -> Dict:
        """Analyze user message to determine intent"""
        message_lower = message.lower()
        
        # Order intent
        order_keywords = ['order', 'want', 'get', 'buy', 'add', 'like']
        if any(keyword in message_lower for keyword in order_keywords):
            # Try to extract meal names/IDs
            meal_ids = self._extract_meal_ids(message)
            return {
                'type': 'order',
                'meal_ids': meal_ids,
                'confidence': 0.8 if meal_ids else 0.5
            }
        
        # Recommendation intent
        rec_keywords = ['recommend', 'suggest', 'what', 'show', 'try', 'good']
        if any(keyword in message_lower for keyword in rec_keywords):
            return {
                'type': 'recommendation',
                'criteria': self._extract_criteria(message),
                'confidence': 0.7
            }
        
        # Information intent
        info_keywords = ['what', 'how', 'tell me', 'describe', 'ingredients']
        if any(keyword in message_lower for keyword in info_keywords):
            return {
                'type': 'information',
                'topic': self._extract_topic(message),
                'confidence': 0.6
            }
        
        return {
            'type': 'general',
            'confidence': 0.3
        }
    
    def _extract_meal_ids(self, message: str) -> List[int]:
        """Extract meal IDs from message - now also handles meal names"""
        meal_ids = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all meals for name matching
        cursor.execute('''
            SELECT id, name, LOWER(name) as lower_name 
            FROM meals
        ''')
        all_meals = cursor.fetchall()
        
        # First, try to extract explicit numbers
        numbers = re.findall(r'\b\d+\b', message)
        for num_str in numbers:
            meal_id = int(num_str)
            cursor.execute("SELECT id FROM meals WHERE id = ?", (meal_id,))
            if cursor.fetchone():
                meal_ids.append(meal_id)
        
        # Then, try to match meal names
        message_lower = message.lower()
        
        for meal_id, meal_name, meal_name_lower in all_meals:
            # Check for exact meal name match
            if meal_name_lower in message_lower:
                meal_ids.append(meal_id)
                continue
            
            # Check for partial matches (words from meal name)
            meal_words = meal_name_lower.split()
            for word in meal_words:
                if len(word) > 3 and word in message_lower:  # Only match words longer than 3 chars
                    meal_ids.append(meal_id)
                    break
        
        conn.close()
        return list(set(meal_ids))  # Remove duplicates
    
    def _extract_criteria(self, message: str) -> Dict:
        """Extract recommendation criteria from message"""
        criteria = {}
        message_lower = message.lower()
        
        # Price criteria
        if 'cheap' in message_lower or 'budget' in message_lower or 'under 10' in message_lower:
            criteria['max_price'] = 10
        elif 'expensive' in message_lower or 'premium' in message_lower:
            criteria['min_price'] = 15
        
        # Calorie criteria
        if 'low calorie' in message_lower or 'light' in message_lower:
            criteria['max_calories'] = 400
        elif 'high calorie' in message_lower or 'heavy' in message_lower:
            criteria['min_calories'] = 600
        
        # Category criteria
        categories = ['seafood', 'chicken', 'beef', 'vegetarian', 'salad', 'pasta', 'burger']
        for cat in categories:
            if cat in message_lower:
                criteria['category'] = cat
                break
        
        return criteria
    
    def _extract_topic(self, message: str) -> str:
        """Extract information topic from message"""
        message_lower = message.lower()
        
        if 'ingredient' in message_lower:
            return 'ingredients'
        elif 'price' in message_lower or 'cost' in message_lower:
            return 'price'
        elif 'calorie' in message_lower:
            return 'calories'
        elif 'allergen' in message_lower:
            return 'allergens'
        
        return 'general'
    
    def _handle_order_intent(self, user_email: str, intent: Dict) -> Dict:
        """Handle order intent - now supports meal names and cart"""
        meal_ids = intent['meal_ids']
        
        if not meal_ids:
            return {
                'response': "I'd be happy to help you order! Could you please specify which meals you'd like by name or ID number? For example: 'I want to order salmon bowl' or 'order meal 1'",
                'suggestions': self._get_meal_suggestions(),
                'intent': 'order_clarification'
            }
        
        # Get meal details
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        meals = []
        for meal_id in meal_ids:
            cursor.execute('''
                SELECT id, name, price, description FROM meals WHERE id = ?
            ''', (meal_id,))
            meal = cursor.fetchone()
            if meal:
                meals.append({
                    'id': meal[0],
                    'name': meal[1],
                    'price': meal[2],
                    'description': meal[3]
                })
        
        conn.close()
        
        if meals:
            total_price = sum(meal['price'] for meal in meals)
            meal_names = ', '.join(meal['name'] for meal in meals)
            
            return {
                'response': f"I've added {meal_names} to your cart. The total is ${total_price:.2f}. Would you like to confirm this order or add more items?",
                'meals': meals,
                'total_price': total_price,
                'intent': 'order_confirmation',
                'order_data': {
                    'meal_ids': meal_ids,
                    'quantities': [1] * len(meal_ids)
                },
                'cart_actions': [
                    'Confirm order',
                    'Add more items',
                    'Remove items',
                    'View cart'
                ]
            }
        
        return {
            'response': "I couldn't find those meals. Here are some popular options:",
            'suggestions': self._get_meal_suggestions(),
            'intent': 'order_not_found'
        }
    
    def _handle_recommendation_intent(self, user_email: str, intent: Dict) -> Dict:
        """Handle recommendation intent"""
        criteria = intent.get('criteria', {})
        
        # Get recommendations
        if criteria:
            recommendations = self._get_criteria_based_recommendations(criteria)
        else:
            recommendations = self.get_personalized_recommendations(user_email)
        
        if recommendations:
            meal_list = '\n'.join([
                f"{rec['id']}: {rec['name']} - ${rec['price']} ({rec['calories']} cal)"
                for rec in recommendations[:5]
            ])
            
            return {
                'response': f"Based on your preferences, I recommend:\n{meal_list}\n\nWould you like more details about any of these?",
                'recommendations': recommendations,
                'intent': 'recommendations'
            }
        
        return {
            'response': "I'd be happy to make recommendations! Let me learn your preferences first. Try ordering some meals or telling me what you like.",
            'intent': 'recommendations_learning'
        }
    
    def _handle_information_intent(self, user_email: str, intent: Dict) -> Dict:
        """Handle information intent"""
        topic = intent.get('topic', 'general')
        
        if topic == 'ingredients':
            return {
                'response': "I can tell you about ingredients! Which meal are you interested in? Please provide the meal ID or name.",
                'intent': 'ingredient_query'
            }
        elif topic == 'price':
            return {
                'response': "I can help with pricing! Our meals range from $8.99 to $18.49. Are you looking for something in a specific price range?",
                'intent': 'price_query'
            }
        elif topic == 'calories':
            return {
                'response': "Our meals range from 350 to 820 calories. Lighter options are under 400 calories, while heavier meals are over 600 calories.",
                'intent': 'calorie_query'
            }
        
        return {
            'response': "I can help you with information about our meals, ingredients, prices, and more. What would you like to know?",
            'intent': 'general_info'
        }
    
    def _handle_general_intent(self, user_email: str, intent: Dict) -> Dict:
        """Handle general chat intent"""
        return {
            'response': "Hello! I'm your intelligent meal assistant. I can help you:\n• Order meals by ID\n• Get personalized recommendations\n• Learn about our menu\n• Track your preferences\n\nWhat would you like to do?",
            'intent': 'greeting'
        }
    
    def _get_meal_suggestions(self, limit: int = 5) -> List[Dict]:
        """Get popular meal suggestions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, price, calories, category 
            FROM meals 
            ORDER BY RANDOM() 
            LIMIT ?
        ''', (limit,))
        
        meals = []
        for row in cursor.fetchall():
            meals.append({
                'id': row[0],
                'name': row[1],
                'price': row[2],
                'calories': row[3],
                'category': row[4]
            })
        
        conn.close()
        return meals
    
    def _get_criteria_based_recommendations(self, criteria: Dict) -> List[Dict]:
        """Get recommendations based on specific criteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT id, name, price, calories, category FROM meals WHERE 1=1"
        params = []
        
        if 'max_price' in criteria:
            query += " AND price <= ?"
            params.append(criteria['max_price'])
        
        if 'min_price' in criteria:
            query += " AND price >= ?"
            params.append(criteria['min_price'])
        
        if 'max_calories' in criteria:
            query += " AND calories <= ?"
            params.append(criteria['max_calories'])
        
        if 'min_calories' in criteria:
            query += " AND calories >= ?"
            params.append(criteria['min_calories'])
        
        if 'category' in criteria:
            query += " AND category = ?"
            params.append(criteria['category'])
        
        query += " ORDER BY RANDOM() LIMIT 5"
        
        cursor.execute(query, params)
        
        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                'id': row[0],
                'name': row[1],
                'price': row[2],
                'calories': row[3],
                'category': row[4]
            })
        
        conn.close()
        return recommendations
    
    def _log_chat_interaction(self, user_email: str, message: str):
        """Log chat interaction for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_training_data 
            (user_email, input_text, context, response)
            VALUES (?, ?, ?, ?)
        ''', (user_email, message, 'chat', ''))
        
        conn.commit()
        conn.close()
    
    def provide_feedback(self, user_email: str, interaction_id: int, rating: int):
        """Provide feedback on AI response for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ai_training_data 
            SET success_rating = ? 
            WHERE id = ?
        ''', (rating, interaction_id))
        
        conn.commit()
        conn.close()
    
    def get_user_insights(self, user_email: str) -> Dict:
        """Get insights about user behavior and preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get top categories
        cursor.execute('''
            SELECT preference_value, weight 
            FROM user_preferences 
            WHERE user_email = ? AND preference_type = 'category'
            ORDER BY weight DESC
            LIMIT 3
        ''', (user_email,))
        top_categories = cursor.fetchall()
        
        # Get recent behaviors
        cursor.execute('''
            SELECT action_type, target_id, timestamp 
            FROM user_behaviors 
            WHERE user_email = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (user_email,))
        recent_behaviors = cursor.fetchall()
        
        # Get order frequency
        cursor.execute('''
            SELECT COUNT(*) 
            FROM user_behaviors 
            WHERE user_email = ? AND action_type = 'order'
        ''', (user_email,))
        order_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'top_categories': [cat[0] for cat in top_categories],
            'recent_behaviors': recent_behaviors,
            'order_count': order_count,
            'learning_progress': min(order_count * 10, 100)  # Simple progress metric
        }
