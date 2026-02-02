import time
from .order_manager import load_orders, save_orders

def get_tracking(order_id):
    orders = load_orders()
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        return None

    now = int(time.time())
    elapsed = now - order["timestamp"]
    stage = min(elapsed // 20, 3)

    statuses = ["Preparing", "Packed", "Out for Delivery", "Delivered"]
    order["status"] = statuses[stage]

    save_orders(orders)
    return order
