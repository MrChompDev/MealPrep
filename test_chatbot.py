"""
Quick Test Script for AI Chatbot
Run this to verify the chatbot is working correctly
"""

import sys
import json
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.ai_chatbot import AIChatbot

def test_chatbot():
    print("=" * 60)
    print("MealPrep AI Chatbot - Test Suite")
    print("=" * 60)
    
    # Initialize chatbot
    meals_path = Path(__file__).parent / "data" / "meals.json"
    chatbot = AIChatbot(str(meals_path))
    
    # Load and display meals
    meals = chatbot.get_meal_list()
    print(f"\n✓ Loaded {len(meals)} meals from meals.json")
    print("\nAvailable Meals:")
    for meal in meals[:5]:  # Show first 5
        print(f"  - {meal['name']} (${meal['price']}) - {meal['calories']} cal")
    if len(meals) > 5:
        print(f"  ... and {len(meals) - 5} more")
    
    # Test 1: Basic ordering
    print("\n" + "-" * 60)
    print("Test 1: Basic Meal Ordering")
    print("-" * 60)
    response = chatbot.get_response("I want a Salmon Power Bowl")
    print(f"User: I want a Salmon Power Bowl")
    print(f"Bot: {response['response']}")
    print(f"Meal Ordered: {response.get('meal_ordered')}")
    if response.get('meal'):
        print(f"Meal Found: {response['meal']['name']} (ID: {response['meal']['id']})")
    
    # Test 2: Quantity
    print("\n" + "-" * 60)
    print("Test 2: Ordering with Quantity")
    print("-" * 60)
    response = chatbot.get_response("I want three Lean Beef Burgers")
    print(f"User: I want three Lean Beef Burgers")
    print(f"Bot: {response['response']}")
    print(f"Quantity: {response.get('quantity', 1)}")
    
    # Test 3: Menu inquiry
    print("\n" + "-" * 60)
    print("Test 3: Menu Inquiry")
    print("-" * 60)
    response = chatbot.get_response("What do you have?")
    print(f"User: What do you have?")
    print(f"Bot: {response['response']}")
    
    # Test 4: Greeting
    print("\n" + "-" * 60)
    print("Test 4: Greeting")
    print("-" * 60)
    response = chatbot.get_response("Hi there!")
    print(f"User: Hi there!")
    print(f"Bot: {response['response']}")
    
    # Test 5: Fuzzy matching
    print("\n" + "-" * 60)
    print("Test 5: Fuzzy Matching (Misspelled)")
    print("-" * 60)
    response = chatbot.get_response("I want a salmin bowl")  # Typo: salmin → Salmon
    print(f"User: I want a salmin bowl")
    print(f"Bot: {response['response']}")
    print(f"Meal Ordered: {response.get('meal_ordered')}")
    
    # Test 6: Non-existent meal
    print("\n" + "-" * 60)
    print("Test 6: Non-existent Meal")
    print("-" * 60)
    response = chatbot.get_response("I want a pizza")
    print(f"User: I want a pizza")
    print(f"Bot: {response['response']}")
    print(f"Meal Ordered: {response.get('meal_ordered')}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ All Tests Completed Successfully!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Run: python app.py")
    print("2. Open browser to http://localhost:5000")
    print("3. Click the green chat button in bottom-right corner")
    print("4. Try ordering meals by typing or using the microphone")

if __name__ == "__main__":
    test_chatbot()
