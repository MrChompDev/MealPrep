import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mealprep.db"

def create_fake_reviews():
    """Create fake reviews for meals"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all meals
    cursor.execute("SELECT id, name FROM meals")
    meals = cursor.fetchall()
    
    # Fake user names
    fake_users = [
        "john.doe@email.com", "jane.smith@email.com", "mike.wilson@email.com",
        "sarah.jones@email.com", "david.brown@email.com", "emma.davis@email.com",
        "chris.miller@email.com", "lisa.garcia@email.com", "tom.rodriguez@email.com",
        "amy.martinez@email.com"
    ]
    
    # Fake review comments
    positive_comments = [
        "Absolutely delicious! Fresh ingredients and perfect portion size.",
        "Best meal I've had all week. Highly recommend!",
        "So flavorful and satisfying. Will definitely order again.",
        "Perfect balance of nutrients and taste. Love it!",
        "Fresh, healthy, and tastes amazing. 5 stars!",
        "Great quality and fast delivery. Very impressed!",
        "Exceeded my expectations. Will become a regular!",
        "Tastes like homemade but better. Fantastic!",
        "Healthy, delicious, and convenient. Perfect combo!",
        "Outstanding quality and flavor. Highly recommend!"
    ]
    
    neutral_comments = [
        "Good meal, decent portion size.",
        "Pretty tasty, could use a bit more seasoning.",
        "Solid choice, nothing amazing but good.",
        "Decent option for a quick meal.",
        "Average quality but convenient.",
        "Not bad, would order again occasionally.",
        "Okay meal, meets expectations.",
        "Fair price for what you get.",
        "Standard quality, nothing special.",
        "Acceptable meal, could be better."
    ]
    
    negative_comments = [
        "A bit disappointing, expected better quality.",
        "Portion was smaller than anticipated.",
        "Flavor was a bit bland for my taste.",
        "Not worth the price in my opinion.",
        "Delivery took longer than expected.",
        "Meal was okay but not great.",
        "Wouldn't order this particular meal again.",
        "Below average experience.",
        "Needs improvement in flavor and quality.",
        "Not satisfied with this order."
    ]
    
    # Create reviews
    for meal_id, meal_name in meals:
        # Each meal gets 3-8 reviews
        num_reviews = random.randint(3, 8)
        
        for _ in range(num_reviews):
            user_email = random.choice(fake_users)
            rating = random.choices(
                [5, 4, 3, 2, 1],
                weights=[0.4, 0.3, 0.15, 0.1, 0.05],  # Mostly positive
                k=1
            )[0]
            
            # Choose comment based on rating
            if rating >= 4:
                comment = random.choice(positive_comments)
            elif rating == 3:
                comment = random.choice(neutral_comments)
            else:
                comment = random.choice(negative_comments)
            
            # Random date within last 3 months
            days_ago = random.randint(1, 90)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute('''
                INSERT OR IGNORE INTO reviews 
                (meal_id, user_email, rating, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (meal_id, user_email, rating, comment, created_at.isoformat()))
    
    conn.commit()
    conn.close()
    print("Fake reviews created successfully!")

def create_fake_suggestions():
    """Create fake suggestions for users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all meals and users
    cursor.execute("SELECT id, name, category FROM meals")
    meals = cursor.fetchall()
    
    cursor.execute("SELECT email FROM users")
    users = cursor.fetchall()
    
    suggestion_reasons = [
        "Based on your past orders",
        "Popular in your area",
        "Matches your dietary preferences",
        "Highly rated by similar users",
        "New addition you might like",
        "Trending this week",
        "Chef's recommendation",
        "Perfect for your taste profile",
        "Healthy choice for you",
        "Great value option"
    ]
    
    # Create suggestions for each user
    for user_email, in users:
        # Each user gets 5-10 suggestions
        num_suggestions = random.randint(5, 10)
        selected_meals = random.sample(meals, min(num_suggestions, len(meals)))
        
        for meal_id, meal_name, category in selected_meals:
            reason = random.choice(suggestion_reasons)
            confidence = random.uniform(0.6, 0.95)  # High confidence
            created_at = datetime.now() - timedelta(hours=random.randint(1, 72))
            
            cursor.execute('''
                INSERT OR IGNORE INTO suggestions 
                (meal_id, suggested_for_email, reason, confidence, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (meal_id, user_email[0], reason, confidence, created_at.isoformat()))
    
    conn.commit()
    conn.close()
    print("Fake suggestions created successfully!")

if __name__ == "__main__":
    create_fake_reviews()
    create_fake_suggestions()
