import json
import os
import time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def create_order(user_email, meals, customer):
    orders = load_orders()
    order_id = f"MP-{len(orders) + 1:05d}"
    timestamp = int(time.time())

    order = {
        "order_id": order_id,
        "user": user_email,
        "meals": meals,
        "customer": customer,
        "status": "Preparing",
        "eta": "18:45",
        "driver": "Sam Lee – 0400 123 456",
        "timestamp": timestamp
    }

    orders.append(order)
    save_orders(orders)
    return order

def get_orders_for_user(email):
    orders = load_orders()
    return [o for o in orders if o["user"] == email]
