"""
AI Chatbot Manager - Handles conversation and meal ordering via chat/voice
"""
import json
import re
from pathlib import Path
from difflib import get_close_matches


class AIChatbot:
    def __init__(self, meals_json_path):
        self.meals_path = meals_json_path
        self.meals = self._load_meals()
        self.conversation_history = []
    
    def _load_meals(self):
        """Load meals from JSON file"""
        try:
            with open(self.meals_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def find_meal(self, query):
        """
        Find a meal by name (with fuzzy matching)
        Returns the meal object if found, None otherwise
        """
        meal_names = [m['name'] for m in self.meals]
        
        # Exact match first
        for meal in self.meals:
            if meal['name'].lower() == query.lower():
                return meal
        
        # Fuzzy match
        matches = get_close_matches(query.lower(), [m.lower() for m in meal_names], n=1, cutoff=0.6)
        if matches:
            for meal in self.meals:
                if meal['name'].lower() == matches[0]:
                    return meal
        
        return None
    
    def extract_meal_request(self, user_message):
        """
        Parse user message to extract meal ordering intent
        Returns (meal_object, quantity) or (None, 0)
        """
        # Look for common ordering patterns
        ordering_keywords = ['i want', 'i need', 'add', 'get me', 'order', 'buy', 'give me', 'can i have']
        
        message_lower = user_message.lower()
        
        # Check if it's an ordering request
        is_ordering = any(keyword in message_lower for keyword in ordering_keywords)
        
        if not is_ordering:
            return None, 0
        
        # Extract quantity
        quantity = 1
        quantity_words = {
            'one': 1, '1': 1,
            'two': 2, '2': 2,
            'three': 3, '3': 3,
            'four': 4, '4': 4,
            'five': 5, '5': 5,
            'six': 6, '6': 6,
            'dozen': 12, '12': 12
        }
        
        for word, num in quantity_words.items():
            if word in message_lower:
                quantity = num
                break
        
        # Extract meal name by removing ordering keywords
        meal_query = user_message
        for keyword in ordering_keywords:
            meal_query = meal_query.lower().replace(keyword, '').strip()
        
        # Remove quantity words
        for word in quantity_words.keys():
            meal_query = meal_query.replace(word, '').strip()
        
        # Try to find the meal
        meal = self.find_meal(meal_query)
        
        return meal, quantity
    
    def get_response(self, user_message):
        """
        Generate AI response to user message
        Returns dict with 'response' text, 'meal_ordered' (optional), 'quantity' (optional)
        """
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Check if user is trying to order
        meal, quantity = self.extract_meal_request(user_message)
        
        response_data = {}
        
        if meal:
            # Meal was found
            response = (
                f"Great choice! I found the {meal['name']} for you. "
                f"It's ${meal['price']:.2f} and has {meal['calories']} calories. "
                f"I'm adding {quantity} to your cart!"
            )
            response_data = {
                'response': response,
                'meal_ordered': True,
                'meal': meal,
                'quantity': quantity
            }
        else:
            # Check if user is asking about a meal in general
            if any(word in user_message.lower() for word in ['what', 'menu', 'do you have', 'categories', 'options']):
                categories = list(set([m.get('category', 'Other') for m in self.meals]))
                response = (
                    f"We have delicious options in these categories: {', '.join(categories)}. "
                    f"Just ask for a meal name and I'll add it to your cart!"
                )
            elif any(word in user_message.lower() for word in ['hello', 'hi', 'hey', 'greet']):
                response = "Hi there! I'm your AI meal ordering assistant. Just tell me what meal you'd like and I'll add it to your cart!"
            elif any(word in user_message.lower() for word in ['price', 'cost', 'how much']):
                response = "I can help with pricing! Just ask for a specific meal and I'll tell you the price."
            else:
                response = (
                    f"I didn't quite understand that. Try saying something like 'I want a Salmon Power Bowl' "
                    f"or 'add Veggie Protein Bowl'. What would you like to order?"
                )
            
            response_data = {
                'response': response,
                'meal_ordered': False
            }
        
        self.conversation_history.append({
            'role': 'assistant',
            'content': response_data.get('response', response)
        })
        
        return response_data
    
    def get_meal_list(self):
        """Return list of all available meals"""
        return self.meals
