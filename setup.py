#!/usr/bin/env python3
"""
Setup script for the Intelligent Meal Prep Ordering System
This script will:
1. Create the SQLite database
2. Migrate existing JSON data to SQL
3. Initialize the AI system
4. Start the application
"""

import sys
import os
from pathlib import Path

def run_setup():
    print("🍽️  Setting up Intelligent Meal Prep Ordering System...")
    
    # Step 1: Create database
    print("\n📊 Creating database...")
    try:
        from create_db import create_database
        create_database()
        print("✅ Database created successfully")
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False
    
    # Step 2: Migrate data
    print("\n📦 Migrating JSON data to SQL...")
    try:
        from migrate_json_to_sql import migrate_json_to_sql
        migrate_json_to_sql()
        print("✅ Data migration completed")
    except Exception as e:
        print(f"❌ Data migration failed: {e}")
        return False
    
    # Step 3: Initialize AI system
    print("\n🤖 Initializing AI system...")
    try:
        from intelligent_ai import IntelligentAI
        ai = IntelligentAI()
        print("✅ AI system initialized")
    except Exception as e:
        print(f"❌ AI initialization failed: {e}")
        return False
    
    # Step 4: Test database connection
    print("\n🔍 Testing database connection...")
    try:
        from database_manager import DatabaseManager
        db = DatabaseManager()
        meals = db.get_all_meals()
        print(f"✅ Database connection successful - found {len(meals)} meals")
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 Starting the application...")
    print("📱 The app will be available at: http://localhost:5000")
    print("🤖 AI features include:")
    print("   • Personalized meal recommendations")
    print("   • User behavior tracking")
    print("   • Intelligent chatbot")
    print("   • Learning from user interactions")
    
    return True

def start_app():
    """Start the Flask application"""
    try:
        import app
        print("\n🌐 Starting web server...")
        app.app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Please run this script from the project directory containing app.py")
        sys.exit(1)
    
    # Run setup
    if run_setup():
        # Start the app
        start_app()
    else:
        print("\n❌ Setup failed. Please check the errors above and try again.")
        sys.exit(1)
