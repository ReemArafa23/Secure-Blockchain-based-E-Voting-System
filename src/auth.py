import json
import os
import hashlib
import getpass
from reporting import log_action

# ====== COMMON PATH SETUP ======
# project root ( .. from src/ )
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
# ================================

def _load_users():
    print("DEBUG USERS_FILE:", USERS_FILE)  # <-- TEMP DEBUG
    if not os.path.exists(USERS_FILE):
        print("DEBUG: users.json does NOT exist")
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
    print("DEBUG: loaded", len(users), "users")
    return users

def _save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def _generate_salt():
    """Generate a random salt as hex string."""
    return os.urandom(16).hex()


def _hash_password(password: str, salt: str) -> str:
    """Return SHA-256(salt + password) as hex digest."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def register_user():
    """
    Interactive registration.
    - If there is no admin yet, the first created user becomes admin.
    - Later users become voters.
    """
    users = _load_users()

    # Check if there is already an admin user
    has_admin = any(u.get("role") == "admin" for u in users)

    print("\n=== Register New User ===")
    username = input("Choose a username: ").strip()

    # Check if username already exists
    if any(u["username"] == username for u in users):
        print("❌ Username already exists. Try another one.")
        return

    # Ask for password (hidden input)
    password = getpass.getpass("Choose a password: ").strip()
    confirm = getpass.getpass("Confirm password: ").strip()

    if password != confirm:
        print("❌ Passwords do not match.")
        return

    if len(password) < 4:
        print("❌ Password too short (minimum 4 characters for this demo).")
        return

    # Decide role
    if not has_admin:
        print("\nNo admin exists yet. This user will be created as ADMIN.")
        role = "admin"
    else:
        role = "voter"   # All next users are voters by default

    salt = _generate_salt()
    password_hash = _hash_password(password, salt)

    new_user = {
        "username": username,
        "password_hash": password_hash,
        "salt": salt,
        "role": role
    }
    users.append(new_user)
    _save_users(users)

    log_action(username, "REGISTER", f"role={role}")
    print(f"✅ User '{username}' registered successfully as {role.upper()}.")


def login_user():
    """
    Interactive login.
    Returns the user dict if success, or None if failed.
    """
    users = _load_users()

    print("\n=== Login ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    # Find user
    user = next((u for u in users if u["username"] == username), None)
    if user is None:
        print("❌ No such user.")
        return None

    expected_hash = user["password_hash"]
    salt = user["salt"]
    entered_hash = _hash_password(password, salt)

    if entered_hash != expected_hash:
        print("❌ Incorrect password.")
        return None

    print(f"✅ Logged in as {user['username']} ({user['role']}).")
    log_action(username, "LOGIN", f"role={user['role']}")
    return user