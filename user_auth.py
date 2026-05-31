"""
Auth module — SQLite + bcrypt user management + session tokens.
Handles registration, login, password verification, and persistent sessions.
"""

import sqlite3
import bcrypt
import secrets
import re
import os
from datetime import datetime, timedelta

# Use /tmp on cloud platforms (Streamlit Cloud, Render, etc.)
# where the app directory may be read-only
_base = "/tmp" if os.path.exists("/tmp") and not os.access(os.path.dirname(os.path.abspath(__file__)), os.W_OK) else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_base, "users.db")


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Persistent login sessions — token stored in browser cookie
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT PRIMARY KEY,
                username   TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        conn.commit()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ── User auth ─────────────────────────────────────────────────────────────────

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    email    = email.strip().lower()

    if len(username) < 2:
        return False, "Username must be at least 2 characters."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, _hash_password(password)),
            )
            conn.commit()
        return True, "Account created! You can now sign in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except Exception as e:
        return False, f"Registration failed: {e}"


def login_user(email: str, password: str) -> tuple[bool, str, str]:
    email = email.strip().lower()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT username, password_hash FROM users WHERE email = ?", (email,)
            ).fetchone()
        if not row:
            return False, "", "No account found with this email."
        username, hashed = row
        if _verify_password(password, hashed):
            return True, username, ""
        return False, "", "Incorrect password."
    except Exception as e:
        return False, "", f"Login error: {e}"


# ── Session tokens (remember me) ──────────────────────────────────────────────

def create_session(username: str, days: int = 30) -> str:
    """Generate a secure session token and store it. Returns the token."""
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(days=days)
    with sqlite3.connect(DB_PATH) as conn:
        # Clean up any expired sessions first
        conn.execute("DELETE FROM sessions WHERE expires_at < datetime('now')")
        conn.execute(
            "INSERT INTO sessions (token, username, expires_at) VALUES (?, ?, ?)",
            (token, username, expires.isoformat()),
        )
        conn.commit()
    return token


def get_session_user(token: str) -> str | None:
    """Return username if token is valid and not expired, else None."""
    if not token:
        return None
    try:
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT username FROM sessions WHERE token = ? AND expires_at > datetime('now')",
                (token,),
            ).fetchone()
        return row[0] if row else None
    except Exception:
        return None


def delete_session(token: str) -> None:
    """Delete a session token on logout."""
    if not token:
        return
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
    except Exception:
        pass
