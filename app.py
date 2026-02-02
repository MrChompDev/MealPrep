import http.server
import socketserver
import os
import json
import time
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from urllib.parse import urlparse, parse_qs

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_FILE = os.path.join(DATA_DIR, "users.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
MEALS_FILE = os.path.join(DATA_DIR, "meals.json")
SUBS_FILE = os.path.join(DATA_DIR, "subscriptions.json")


def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_users():
    users = load_json(USERS_FILE)
    if not isinstance(users, list):
        return []
    return [u for u in users if isinstance(u, dict)]


def save_users(users):
    save_json(USERS_FILE, users)


def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def get_cookies(header):
    cookies = {}
    if not header:
        return cookies
    for p in header.split(";"):
        if "=" in p:
            k, v = p.strip().split("=", 1)
            cookies[k] = v
    return cookies


def get_user_by_session(token):
    if not token:
        return None
    users = load_users()
    for u in users:
        if u.get("session") == token:
            return u
    return None


def send_email(to, subject, body):
    if not to:
        return
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "mealprep@example.com"
        msg["To"] = to

        # Replace with your real SMTP details
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("YOUR_EMAIL@gmail.com", "YOUR_APP_PASSWORD")
            server.send_message(msg)
    except Exception as e:
        print("Email error:", e)


class Handler(http.server.SimpleHTTPRequestHandler):

    def json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def get_current_user(self):
        cookies = get_cookies(self.headers.get("Cookie"))
        return get_user_by_session(cookies.get("session"))

    def require_admin(self):
        user = self.get_current_user()
        return user and user.get("is_admin")

    def serve_template(self, filename):
        filepath = os.path.join(TEMPLATES_DIR, filename)
        if not os.path.exists(filepath):
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Meals API – all meals
        if path == "/api/meals":
            meals = load_json(MEALS_FILE)
            return self.json_response(meals)

        # Single meal
        if path.startswith("/api/meals/"):
            meal_id = path.split("/")[-1]
            meals = load_json(MEALS_FILE)
            meal = next((m for m in meals if str(m.get("id")) == meal_id), None)
            if meal:
                return self.json_response(meal)
            return self.json_response({"error": "not found"}, 404)

        # Tracking API
        if path.startswith("/api/track/"):
            order_id = path.split("/")[-1]
            orders = load_json(ORDERS_FILE)
            order = next((o for o in orders if o.get("order_id") == order_id), None)
            if not order:
                return self.json_response({"error": "not found"}, 404)
            now = int(time.time())
            elapsed = max(0, now - order.get("timestamp", now))
            stage = min(elapsed // 20, 3)
            statuses = ["Preparing", "Packed", "Out for Delivery", "Delivered"]
            order["status"] = statuses[stage]

            # Fake route coordinates
            route = [
                {"lat": -28.000, "lng": 153.430},
                {"lat": -28.010, "lng": 153.440},
                {"lat": -28.020, "lng": 153.450},
                {"lat": -28.030, "lng": 153.460}
            ]
            order["location"] = route[stage]

            save_json(ORDERS_FILE, orders)
            return self.json_response(order)

        # Subscription plans
        if path == "/api/subscriptions":
            return self.json_response(load_json(SUBS_FILE))

        # My orders
        if path == "/api/my_orders":
            user = self.get_current_user()
            if not user:
                return self.json_response({"error": "not logged in"}, 401)
            orders = load_json(ORDERS_FILE)
            user_orders = [o for o in orders if o.get("user") == user["email"]]
            return self.json_response(user_orders)

        # Admin APIs
        if path == "/api/admin/orders":
            if not self.require_admin():
                return self.json_response({"error": "forbidden"}, 403)
            return self.json_response(load_json(ORDERS_FILE))

        if path == "/api/admin/stats":
            if not self.require_admin():
                return self.json_response({"error": "forbidden"}, 403)
            orders = load_json(ORDERS_FILE)
            stats = {
                "total": len(orders),
                "delivered": sum(1 for o in orders if o["status"] == "Delivered"),
                "unpaid": sum(1 for o in orders if not o.get("paid"))
            }
            return self.json_response(stats)

        if path == "/api/admin/meals":
            if not self.require_admin():
                return self.json_response({"error": "forbidden"}, 403)
            return self.json_response(load_json(MEALS_FILE))

        if path == "/api/admin/subscriptions_stats":
            if not self.require_admin():
                return self.json_response({"error": "forbidden"}, 403)

            users = load_users()
            subs = load_json(SUBS_FILE)

            active = [u for u in users if u.get("subscription_paid")]
            cancelled = [u for u in users if not u.get("subscription_paid") and u.get("subscription")]

            revenue = 0.0
            for u in active:
                plan = next((p for p in subs if p.get("id") == u.get("subscription")), None)
                if plan:
                    revenue += plan.get("price", 0.0)

            stats = {
                "active_subscriptions": len(active),
                "cancelled_subscriptions": len(cancelled),
                "estimated_weekly_revenue": revenue
            }
            return self.json_response(stats)

        # Profile
        if path == "/api/profile":
            user = self.get_current_user()
            if not user:
                return self.json_response({"error": "not logged in"}, 401)
            return self.json_response({
                "email": user["email"],
                "name": user.get("name", ""),
                "address": user.get("address", ""),
                "phone": user.get("phone", "")
            })

        # My subscription info
        if path == "/api/my_subscription":
            user = self.get_current_user()
            if not user:
                return self.json_response({"error": "not logged in"}, 401)
            subs = load_json(SUBS_FILE)
            plan = None
            if user.get("subscription"):
                plan = next((p for p in subs if p.get("id") == user["subscription"]), None)
            return self.json_response({
                "plan": plan,
                "meals": user.get("subscription_meals", []),
                "next_delivery": user.get("subscription_renewal_ts")
            })

        # HTML pages
        pages = {
            "/": "index.html",
            "/index.html": "index.html",
            "/meals": "meals.html",
            "/meal": "meal_detail.html",
            "/checkout": "checkout.html",
            "/tracking": "tracking.html",
            "/login": "login.html",
            "/register": "register.html",
            "/my_orders": "my_orders.html",
            "/profile": "profile.html",
            "/admin": "admin.html",
            "/reset_request": "reset_request.html",
            "/reset_password": "reset_password.html",
            "/subscription": "subscription.html",
            "/my_subscription": "my_subscription.html"
        }

        if path in pages:
            return self.serve_template(pages[path])

        # Logout
        if path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "session=; Path=/; Max-Age=0; HttpOnly")
            self.send_header("Location", "/")
            self.end_headers()
            return

        # Static
        if path.startswith("/static/"):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        data = json.loads(body) if body else {}

        # Register
        if path == "/api/register":
            email = data.get("email", "").strip().lower()
            password = data.get("password", "")
            if not email or not password:
                return self.json_response({"success": False}, 400)
            users = load_users()
            if any(u.get("email") == email for u in users):
                return self.json_response({"success": False, "message": "Email exists"}, 400)
            users.append({
                "email": email,
                "password": hash_password(password),
                "session": None,
                "name": "",
                "address": "",
                "phone": "",
                "reset_token": None,
                "is_admin": False,
                "subscription": None,
                "subscription_meals": [],
                "subscription_paid": False,
                "subscription_card_last4": None,
                "subscription_renewal_ts": None
            })
            save_users(users)
            return self.json_response({"success": True})

        # Login
        if path == "/api/login":
            email = data.get("email", "").strip().lower()
            password = data.get("password", "")
            users = load_users()
            for u in users:
                if u.get("email") == email:
                    # Admin login (plain text)
                    if u.get("is_admin") and u.get("password") == password:
                        token = secrets.token_hex(16)
                        u["session"] = token
                        save_users(users)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Set-Cookie", f"session={token}; Path=/; HttpOnly")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True, "admin": True}).encode())
                        return
                    # User login (hashed)
                    if not u.get("is_admin") and u.get("password") == hash_password(password):
                        token = secrets.token_hex(16)
                        u["session"] = token
                        save_users(users)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Set-Cookie", f"session={token}; Path=/; HttpOnly")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True, "admin": False}).encode())
                        return
            return self.json_response({"success": False}, 401)

        # Profile update
        if path == "/api/profile":
            user = self.get_current_user()
            if not user:
                return self.json_response({"success": False}, 401)
            users = load_users()
            for u in users:
                if u.get("email") == user["email"]:
                    u["name"] = data.get("name", u.get("name", ""))
                    u["address"] = data.get("address", u.get("address", ""))
                    u["phone"] = data.get("phone", u.get("phone", ""))
                    break
            save_users(users)
            return self.json_response({"success": True})

        # Reset request
        if path == "/api/reset_request":
            email = data.get("email", "").strip().lower()
            users = load_users()
            token = secrets.token_hex(16)
            for u in users:
                if u.get("email") == email:
                    u["reset_token"] = token
                    save_users(users)
                    return self.json_response({"success": True, "token": token})
            return self.json_response({"success": False}, 404)

        # Reset password
        if path == "/api/reset_password":
            token = data.get("token", "")
            new_pw = data.get("password", "")
            users = load_users()
            for u in users:
                if u.get("reset_token") == token:
                    u["password"] = hash_password(new_pw)
                    u["reset_token"] = None
                    save_users(users)
                    return self.json_response({"success": True})
            return self.json_response({"success": False}, 400)

        # Create order
        if path == "/api/orders":
            user = self.get_current_user()
            email = user["email"] if user else data.get("customer", {}).get("email")
            meals = data.get("meals", [])
            customer = data.get("customer", {})
            orders = load_json(ORDERS_FILE)
            order_id = f"MP-{len(orders) + 1:05d}"
            ts = int(time.time())
            order = {
                "order_id": order_id,
                "user": email,
                "meals": meals,
                "customer": customer,
                "status": "Preparing",
                "eta": "18:45",
                "driver": "Sam Lee – 0400 123 456",
                "timestamp": ts,
                "paid": False
            }
            orders.append(order)
            save_json(ORDERS_FILE, orders)
            return self.json_response(order, 201)

        # Pay order
        if path == "/api/pay":
            order_id = data.get("order_id")
            orders = load_json(ORDERS_FILE)
            for o in orders:
                if o.get("order_id") == order_id:
                    o["paid"] = True
                    save_json(ORDERS_FILE, orders)
                    return self.json_response({"success": True})
            return self.json_response({"success": False}, 404)

        # Subscribe (basic)
        if path == "/api/subscribe":
            user = self.get_current_user()
            if not user:
                return self.json_response({"success": False}, 401)
            plan_id = data.get("plan_id")
            users = load_users()
            for u in users:
                if u.get("email") == user["email"]:
                    u["subscription"] = plan_id
                    break
            save_users(users)
            return self.json_response({"success": True})

        # Pay subscription (store billing info)
        if path == "/api/pay_subscription":
            user = self.get_current_user()
            if not user:
                return self.json_response({"success": False}, 401)

            plan_id = data.get("plan_id")
            card_last4 = data.get("card_last4", "0000")

            users = load_users()
            now = int(time.time())

            for u in users:
                if u.get("email") == user["email"]:
                    u["subscription"] = plan_id
                    u["subscription_paid"] = True
                    u["subscription_card_last4"] = card_last4
                    u["subscription_renewal_ts"] = now + 7 * 24 * 3600
                    break

            save_users(users)
            return self.json_response({"success": True})

        # Save subscription meals (choose 5)
        if path == "/api/subscription_meals":
            user = self.get_current_user()
            if not user:
                return self.json_response({"success": False}, 401)
            meal_ids = data.get("meal_ids", [])
            if len(meal_ids) != 5:
                return self.json_response(
                    {"success": False, "message": "You must select exactly 5 meals."},
                    400
                )
            users = load_users()
            for u in users:
                if u.get("email") == user["email"]:
                    u["subscription_meals"] = meal_ids
                    break
            save_users(users)
            return self.json_response({"success": True})

        # Cancel subscription
        if path == "/api/subscription_cancel":
            user = self.get_current_user()
            if not user:
                return self.json_response({"success": False}, 401)
            users = load_users()
            for u in users:
                if u.get("email") == user["email"]:
                    u["subscription"] = None
                    u["subscription_meals"] = []
                    u["subscription_paid"] = False
                    u["subscription_card_last4"] = None
                    u["subscription_renewal_ts"] = None
                    break
            save_users(users)
            return self.json_response({"success": True})

        # Run weekly subscription deliveries
        if path == "/api/subscriptions_run":
            users = load_users()
            meals = load_json(MEALS_FILE)
            orders = load_json(ORDERS_FILE)

            now = int(time.time())
            created = []

            for u in users:
                if not u.get("subscription_paid"):
                    continue
                if not u.get("subscription_meals"):
                    continue

                selected_meals = []
                for mid in u["subscription_meals"]:
                    m = next((x for x in meals if x.get("id") == mid), None)
                    if m:
                        selected_meals.append({
                            "id": m["id"],
                            "name": m["name"],
                            "price": m["price"]
                        })

                if not selected_meals:
                    continue

                order_id = f"SUB-{len(orders) + 1:05d}"
                order = {
                    "order_id": order_id,
                    "user": u["email"],
                    "meals": selected_meals,
                    "customer": {
                        "name": u.get("name", u["email"]),
                        "address": u.get("address", ""),
                        "email": u["email"]
                    },
                    "status": "Preparing",
                    "eta": "18:45",
                    "driver": "Sam Lee – 0400 123 456",
                    "timestamp": now,
                    "paid": True,
                    "subscription": True
                }
                orders.append(order)
                created.append(order_id)

                # schedule next renewal
                u["subscription_renewal_ts"] = now + 7 * 24 * 3600

            save_json(ORDERS_FILE, orders)
            save_users(users)
            return self.json_response({"success": True, "created": created})

        # Admin: update order status
        if path == "/api/admin/update_status":
            if not self.require_admin():
                return self.json_response({"error": "forbidden"}, 403)
            order_id = data.get("order_id")
            new_status = data.get("status")
            orders = load_json(ORDERS_FILE)
            for o in orders:
                if o.get("order_id") == order_id:
                    o["status"] = new_status
                    save_json(ORDERS_FILE, orders)
                    if new_status == "Delivered":
                        user_email = o.get("user")
                        meal_names = ", ".join([m["name"] for m in o.get("meals", [])])
                        send_email(
                            user_email,
                            "Your MealPrep Order Has Arrived!",
                            f"Your order {o['order_id']} has been delivered.\nMeals: {meal_names}"
                        )
                    return self.json_response({"success": True})
            return self.json_response({"error": "not found"}, 404)

        # Admin: add meal
        if path == "/api/admin/meals_add":
            if not self.require_admin():
                return self.json_response({"error": "forbidden"}, 403)
            meals = load_json(MEALS_FILE)
            new_meal = data
            if "id" not in new_meal:
                new_meal["id"] = (max((m["id"] for m in meals), default=0) + 1)
            new_meal["subscription"] = data.get("subscription", False)
            meals.append(new_meal)
            save_json(MEALS_FILE, meals)
            return self.json_response({"success": True, "meal": new_meal})

        # Admin: update meal
        if path == "/api/admin/meals_update":
            if not self.require_admin():
                return self.json_response({"error": "forbidden"}, 403)
            meal_id = data.get("id")
            meals = load_json(MEALS_FILE)
            for m in meals:
                if m.get("id") == meal_id:
                    m.update(data)
                    m["subscription"] = data.get("subscription", m.get("subscription", False))
                    save_json(MEALS_FILE, meals)
                    return self.json_response({"success": True, "meal": m})
            return self.json_response({"error": "not found"}, 404)

        # Admin: delete meal
        if path == "/api/admin/meals_delete":
            if not self.require_admin():
                return self.json_response({"error": "forbidden"}, 403)
            meal_id = data.get("id")
            meals = load_json(MEALS_FILE)
            meals = [m for m in meals if m.get("id") != meal_id]
            save_json(MEALS_FILE, meals)
            return self.json_response({"success": True})

        self.send_response(404)
        self.end_headers()

    def translate_path(self, path):
        if path.startswith("/static/"):
            rel = path[len("/static/"):]
            return os.path.join(STATIC_DIR, rel.lstrip("/"))
        return http.server.SimpleHTTPRequestHandler.translate_path(self, path)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving on http://localhost:{PORT}")
        httpd.serve_forever()
