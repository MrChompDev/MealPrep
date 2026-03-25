# models.py
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, Text, Float)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    password_hash = Column(String)
    two_factor = Column(Boolean, default=False)
    profile_pic = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="user")
    chat_logs = relationship("ChatLog", back_populates="user")

class Meal(Base):
    __tablename__ = 'meals'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10,2), nullable=False)
    calories = Column(Integer)
    category = Column(String)
    subscription = Column(Boolean, default=False)
    removable_ingredients = Column(Text)  # JSON array
    allergens = Column(Text)  # JSON array
    week = Column(Integer, default=0)
    image = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String, default='Preparing')
    driver = Column(String, default='John')
    eta = Column(String)
    amount_cents = Column(Integer)
    paid = Column(Boolean, default=False)
    source = Column(String, default='one_off')
    week_start = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    meal_id = Column(Integer, ForeignKey('meals.id'))
    quantity = Column(Integer, default=1)
    unit_price_cents = Column(Integer)
    order = relationship("Order", back_populates="items")

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    plan_id = Column(String, nullable=False)
    addons = Column(Text)  # JSON array
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    next_renewal = Column(DateTime)
    weeks = Column(Text)  # JSON array
    history = Column(Text)  # JSON array

class ChatLog(Base):
    __tablename__ = 'chat_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="chat_logs")

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatConfig(Base):
    __tablename__ = 'chat_config'
    id = Column(Integer, primary_key=True, default=1)
    supported_meal = Column(String)
    trigger_word = Column(String)
    success_response = Column(String)
    fallback_response = Column(String)
    unknown_response = Column(String)
    openrouter_model = Column(String, default='anthropic/claude-3-haiku')
    openrouter_api_key = Column(Text)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Allergy(Base):
    __tablename__ = 'allergies'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Driver(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey('meals.id'))
    user_email = Column(String, ForeignKey('users.email'))
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meal = relationship("Meal")
    user = relationship("User")

class Suggestion(Base):
    __tablename__ = 'suggestions'
    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey('meals.id'))
    suggested_for_email = Column(String, ForeignKey('users.email'))
    reason = Column(String)  # Why this was suggested
    confidence = Column(Float, default=0.0)  # How confident we are
    created_at = Column(DateTime, default=datetime.utcnow)
    viewed = Column(Boolean, default=False)
    accepted = Column(Boolean, default=False)
    
    # Relationships
    meal = relationship("Meal")
    user = relationship("User")
