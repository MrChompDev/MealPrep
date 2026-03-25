import sqlite3
import json
from datetime import datetime
from pathlib import Path
from models import Base

# Database setup
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mealprep.db"

def create_database():
    """Create SQLite database with all necessary tables"""
    DATA_DIR.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT,
            two_factor BOOLEAN DEFAULT FALSE,
            profile_pic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Meals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            calories INTEGER,
            category TEXT,
            subscription BOOLEAN DEFAULT FALSE,
            removable_ingredients TEXT,  -- JSON array
            allergens TEXT,  -- JSON array
            week INTEGER DEFAULT 0,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            status TEXT DEFAULT 'Preparing',
            driver TEXT DEFAULT 'John',
            eta TEXT,
            amount_cents INTEGER,
            paid BOOLEAN DEFAULT FALSE,
            source TEXT DEFAULT 'one_off',
            week_start TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            meal_id INTEGER,
            quantity INTEGER NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (meal_id) REFERENCES meals (id)
        )
    ''')
    
    # Subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            addons TEXT,  -- JSON array
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            next_renewal TIMESTAMP,
            weeks TEXT,  -- JSON array
            history TEXT  -- JSON array
        )
    ''')
    
    # Chat logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # System logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chat config table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_config (
            id INTEGER PRIMARY KEY DEFAULT 1,
            supported_meal TEXT,
            trigger_word TEXT,
            success_response TEXT,
            fallback_response TEXT,
            unknown_response TEXT,
            openrouter_model TEXT DEFAULT 'anthropic/claude-3-haiku',
            openrouter_api_key TEXT
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Allergies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allergies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Drivers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meal_id) REFERENCES meals (id),
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
    ''')
    
    # Suggestions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER NOT NULL,
            suggested_for_email TEXT NOT NULL,
            reason TEXT,
            confidence REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            viewed BOOLEAN DEFAULT FALSE,
            accepted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (meal_id) REFERENCES meals (id),
            FOREIGN KEY (suggested_for_email) REFERENCES users (email)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database created successfully at {DB_PATH}")

if __name__ == "__main__":
    create_database()
