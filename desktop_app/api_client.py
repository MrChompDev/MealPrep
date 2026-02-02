import json
import urllib.request
import http.cookiejar

BASE_URL = "http://localhost:8000"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj)
)

def _get(path):
    req = urllib.request.Request(BASE_URL + path, method="GET")
    with opener.open(req) as resp:
        data = resp.read().decode("utf-8")
        return json.loads(data)

def _post(path, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"}
    )
    with opener.open(req) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)

def login(email, password):
    return _post("/api/login", {"email": email, "password": password})

def get_meals():
    return _get("/api/meals")

def get_meal(meal_id):
    return _get(f"/api/meals/{meal_id}")

def create_order(meals, customer):
    return _post("/api/orders", {"meals": meals, "customer": customer})

def track_order(order_id):
    return _get(f"/api/track/{order_id}")

def get_my_orders():
    return _get("/api/my_orders")

def get_subscriptions():
    return _get("/api/subscriptions")

def subscribe(plan_id):
    return _post("/api/subscribe", {"plan_id": plan_id})

def logout():
    try:
        _get("/logout")
    except Exception:
        pass

# admin
def admin_get_orders():
    return _get("/api/admin/orders")

def admin_update_status(order_id, status):
    return _post("/api/admin/update_status", {"order_id": order_id, "status": status})

def admin_stats():
    return _get("/api/admin/stats")

def admin_get_meals():
    return _get("/api/admin/meals")

def admin_add_meal(meal):
    return _post("/api/admin/meals_add", meal)

def admin_update_meal(meal):
    return _post("/api/admin/meals_update", meal)

def admin_delete_meal(meal_id):
    return _post("/api/admin/meals_delete", {"id": meal_id})
