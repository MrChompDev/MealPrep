import json
import os
import hashlib
import secrets

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    users = load_users()
    if any(u["email"] == email for u in users):
        return False, "Email already exists"

    user = {
        "email": email,
        "password": hash_password(password),
        "session": None
    }
    users.append(user)
    save_users(users)
    return True, "Registered"

def login_user(email, password):
    users = load_users()
    hashed = hash_password(password)

    for u in users:
        if u["email"] == email and u["password"] == hashed:
            token = secrets.token_hex(16)
            u["session"] = token
            save_users(users)
            return True, token

    return False, None

def logout_user(token):
    users = load_users()
    for u in users:
        if u["session"] == token:
            u["session"] = None
            save_users(users)
            return True
    return False

def get_user_by_session(token):
    users = load_users()
    for u in users:
        if u["session"] == token:
            return u
    return None
