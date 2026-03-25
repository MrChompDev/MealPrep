import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mealprep.db"

def hash_password(password):
    """Hash password using SHA256"""
    if password is None:
        return None
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_json(filename):
    """Load JSON data from data directory"""
    path = DATA_DIR / filename
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def migrate_json_to_sql():
    """Migrate all JSON data to SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Migrate users
        print("Migrating users...")
        users = load_json("users.json")
        for user in users:
            print(f"Processing user: {user.get('email')}")
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (email, name, password_hash, two_factor, profile_pic, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user.get("email"),
                user.get("name"),
                user.get("password_hash") or hash_password(user.get("password")),
                False,  # Default two_factor to False
                None,  # Default profile_pic to None
                datetime.now().isoformat()
            ))
        
        # Migrate meals
        print("Migrating meals...")
        meals = load_json("meals.json")
        for meal in meals:
            print(f"Processing meal: {meal.get('name')}")
            cursor.execute('''
                INSERT OR REPLACE INTO meals 
                (id, name, description, price, calories, category, subscription, 
                 removable_ingredients, allergens, week, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                meal.get("id"),
                meal.get("name"),
                meal.get("description", ""),
                meal.get("price"),
                meal.get("calories"),
                meal.get("category"),
                meal.get("subscription", False),
                json.dumps(meal.get("removable_ingredients", [])),
                json.dumps(meal.get("allergens", [])),
                meal.get("week", 0),
                meal.get("created_at", datetime.now().isoformat())
            ))
        
        # Migrate orders
        print("Migrating orders...")
        orders = load_json("orders.json")
        for order in orders:
            print(f"Processing order: {order.get('order_id')}")
            # Get user_id from user email
            user_email = order.get("user", {}).get("email") if isinstance(order.get("user"), dict) else order.get("user")
            cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
            user_result = cursor.fetchone()
            user_id = user_result[0] if user_result else None
            
            # Insert order (only include fields that exist in our schema)
            cursor.execute('''
                INSERT OR REPLACE INTO orders 
                (order_id, user_id, status, driver, eta, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                order.get("order_id"),
                user_id,
                order.get("status", "Preparing"),
                order.get("driver", "John"),
                order.get("eta"),
                "one_off",  # Default source
                datetime.fromtimestamp(order.get("timestamp", datetime.now().timestamp())).isoformat() if order.get("timestamp") else datetime.now().isoformat()
            ))
            
            # Get order ID for order items
            cursor.execute("SELECT id FROM orders WHERE order_id = ?", (order.get("order_id"),))
            order_result = cursor.fetchone()
            order_db_id = order_result[0] if order_result else None
            
            # Insert order items
            if order_db_id and "meals" in order:
                for meal_item in order["meals"]:
                    if isinstance(meal_item, dict):
                        meal_id = meal_item.get("id")
                        quantity = meal_item.get("quantity", 1)
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
        
        # Migrate subscriptions
        print("Migrating subscriptions...")
        subscriptions = load_json("subscriptions_data.json") or []
        for sub in subscriptions:
            print(f"Processing subscription: {sub.get('email')}")
            cursor.execute('''
                INSERT OR REPLACE INTO subscriptions 
                (email, plan_id, addons, active, created_at, next_renewal, weeks, history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sub.get("email"),
                sub.get("plan_id"),
                json.dumps(sub.get("addons", [])),
                sub.get("active", True),
                sub.get("created_at", datetime.now().isoformat()),
                sub.get("next_renewal"),
                json.dumps(sub.get("weeks", [])),
                json.dumps(sub.get("history", []))
            ))
        
        # Migrate chat config
        print("Migrating chat config...")
        chat_config = load_json("chat.json")
        if chat_config:
            cursor.execute('''
                INSERT OR REPLACE INTO chat_config 
                (id, supported_meal, trigger_word, success_response, fallback_response, unknown_response)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (
                chat_config.get("supported_meal"),
                chat_config.get("trigger_word"),
                chat_config.get("success_response"),
                chat_config.get("fallback_response"),
                chat_config.get("unknown_response")
            ))
        
        # Migrate categories
        print("Migrating categories...")
        categories = load_json("categories.json")
        for cat in categories:
            # Handle both string and object formats
            if isinstance(cat, dict):
                cat_name = cat.get("name")
            else:
                cat_name = cat
            
            if cat_name:  # Only insert if we have a valid name
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name)
                    VALUES (?)
                ''', (cat_name,))
        
        # Migrate allergies
        print("Migrating allergies...")
        allergies = load_json("allergies.json")
        for allergy in allergies:
            # Handle both string and object formats
            if isinstance(allergy, dict):
                allergy_name = allergy.get("name")
            else:
                allergy_name = allergy
            
            if allergy_name:  # Only insert if we have a valid name
                cursor.execute('''
                    INSERT OR IGNORE INTO allergies (name)
                    VALUES (?)
                ''', (allergy_name,))
        
        # Migrate drivers
        print("Migrating drivers...")
        drivers = load_json("drivers.json")
        for driver in drivers:
            # Handle both string and object formats
            if isinstance(driver, dict):
                driver_name = driver.get("name")
            else:
                driver_name = driver
            
            if driver_name:  # Only insert if we have a valid name
                cursor.execute('''
                    INSERT OR IGNORE INTO drivers (name)
                    VALUES (?)
                ''', (driver_name,))
        
        conn.commit()
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        print(f"Error details: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        conn.close()
        raise

if __name__ == "__main__":
    migrate_json_to_sql()
