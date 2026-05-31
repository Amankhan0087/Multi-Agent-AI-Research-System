"""
Auth module — SQLite + bcrypt user management.
Handles registration, login, and password verification.
"""

import sqlite3
import bcrypt
import re
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


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
        conn.commit()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


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
