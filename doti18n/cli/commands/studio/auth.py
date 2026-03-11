import hashlib
import inspect
import json
import os
import secrets
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

from microdot.microdot import redirect

SESSION_TTL = int(os.environ.get("DOTI18N_SESSION_TTL", 3600))
MAX_FAILED_ATTEMPTS = int(os.environ.get("DOTI18N_MAX_ATTEMPTS", 24 * 60 * 60))
BAN_TIME = int(os.environ.get("DOTI18N_BAN_TIME", 24 * 60 * 60))
SESSIONS: Dict[str, Dict[str, Any]] = {}
_auth_file: Optional[Path] = None


def _get_auth_file() -> Path:
    """Resolve the auth file path. Uses DOTI18N_AUTH_FILE env var or CWD/studio_users.json."""
    global _auth_file
    if _auth_file is not None:
        return _auth_file
    _auth_file = Path(os.environ.get("DOTI18N_AUTH_FILE", Path.cwd() / "studio_users.json"))
    return _auth_file


def set_auth_file(path: Union[str, Path]):
    """Override the auth file path programmatically."""
    global _auth_file
    _auth_file = Path(path)


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash a password with an optional salt. If no salt is provided, a new one is generated."""
    if salt is None:
        salt = secrets.token_hex(16)

    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()

    return f"{salt}${pwd_hash}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a provided password against the stored hash."""
    if "$" not in stored_password:
        return False
    salt, hash_val = stored_password.split("$", 1)
    return hash_password(provided_password, salt) == stored_password


def load_auth_data() -> dict:
    """Load authentication data including users and banned IPs."""
    auth_file = _get_auth_file()
    if not auth_file.exists():
        return {"users": {}, "banned": {}}

    try:
        with open(auth_file, encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"users": {}, "banned": {}}

            if "users" not in data and "banned" not in data:
                return {"users": data, "banned": {}}

            if "users" not in data:
                data["users"] = {}
            if "banned" not in data:
                data["banned"] = {}

            return data

    except (json.JSONDecodeError, IOError):
        return {"users": {}, "banned": {}}


def save_auth_data(data: dict):
    """Save authentication data including users and banned IPs."""
    auth_file = _get_auth_file()
    with open(auth_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_users() -> dict:
    """Load users from the auth file. Returns an empty dict if the file doesn't exist or is invalid."""
    data: dict = load_auth_data().get("users", {})
    return data if isinstance(data, dict) else {}


def save_users(users: dict):
    """Save users to the auth file. Overwrites existing content. Creates the file if it doesn't exist."""
    data = load_auth_data()
    data["users"] = users
    save_auth_data(data)


def add_user(username: str, password: str):
    """Add a new user. Overwrites an existing user if the username already exists."""
    users = load_users()
    users[username] = hash_password(password)
    save_users(users)


def verify_user(username: str, password: str) -> bool:
    """Verify a user's credentials. Returns True if valid, False otherwise."""
    users = load_users()
    if username not in users:
        return False

    return verify_password(users[username], password)


def is_ip_banned(ip: str) -> bool:
    """Check if an IP address is banned. Clears the ban if the duration has expired."""
    data = load_auth_data()
    banned_info = data["banned"].get(ip)

    if not banned_info:
        return False

    ban_until = banned_info.get("ban_until", 0)

    if ban_until > 0 and time.time() < ban_until:
        return True

    if 0 < ban_until <= time.time():
        del data["banned"][ip]
        save_auth_data(data)

    return False


def record_failed_attempt(ip: str):
    """Record a failed login attempt for an IP. Bans the IP if the max limit is reached."""
    data = load_auth_data()
    banned_info = data["banned"].get(ip, {"attempts": 0, "ban_until": 0})

    if banned_info.get("ban_until", 0) > time.time():
        return

    banned_info["attempts"] += 1

    if banned_info["attempts"] >= MAX_FAILED_ATTEMPTS:
        banned_info["ban_until"] = time.time() + BAN_TIME

    data["banned"][ip] = banned_info
    save_auth_data(data)


def clear_failed_attempts(ip: str):
    """Clear failed login attempts for an IP upon successful login."""
    data = load_auth_data()
    if ip in data["banned"]:
        del data["banned"][ip]
        save_auth_data(data)


def create_session(username: str, ip_address: str) -> str:
    """Create a new session for a user. Returns the session token."""
    token = secrets.token_hex(32)
    SESSIONS[token] = {"username": username, "ip": ip_address, "created_at": time.time()}
    return token


def get_session(token: str, ip_address: Optional[str] = None) -> Optional[str]:
    """Validate a session token and return the associated username if valid. Optionally checks IP address."""
    session = SESSIONS.get(token)
    if not session:
        return None

    created_at: float = session.get("created_at", 0)  # type: ignore[assignment]
    if time.time() - created_at > SESSION_TTL:
        del SESSIONS[token]
        return None

    if ip_address and session.get("ip") != ip_address:
        return None

    username = session.get("username")
    return str(username) if username is not None else None


def delete_session(token: str):
    """Delete a session token, effectively logging the user out."""
    if token in SESSIONS:
        del SESSIONS[token]


def login_required(f: Callable):
    """Protect routes that require authentication."""
    if inspect.iscoroutinefunction(f):

        @wraps(f)
        async def adecorated(request, *args, **kwargs):
            token = request.cookies.get("session")
            if not token or not get_session(token, request.client_addr[0]):
                return redirect("/login")

            return await f(request, *args, **kwargs)

        return adecorated

    @wraps(f)
    def decorated(request, *args, **kwargs):
        token = request.cookies.get("session")
        if not token or not get_session(token, request.client_addr[0]):
            return redirect("/login")

        return f(request, *args, **kwargs)

    return decorated
