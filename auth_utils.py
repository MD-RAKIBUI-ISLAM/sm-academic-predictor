# auth_utils.py

import sqlite3
import hashlib
import re
import streamlit as st
from style_utils import load_css

load_css()


DB_PATH = "users.db"


def init_db():
    """Create the users table if it doesn't exist, and migrate in the
    trial_used column if this is an older database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            institution TEXT NOT NULL,
            registration_number TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            verification_status TEXT DEFAULT 'Pending',
            trial_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    try:
        c.execute("ALTER TABLE users ADD COLUMN trial_used INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists on this database

    conn.close()


def hash_password(password: str) -> str:
    """Simple salted hash. Adequate for a thesis-scale local deployment;
    not intended as production-grade security."""
    salt = "sm_academic_predictor_v1"
    return hashlib.sha256((salt + password).encode()).hexdigest()


def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def signup(full_name, email, institution, registration_number, password):
    """Attempt to create a new account. Returns (success: bool, message: str)."""
    if not all([full_name, email, institution, registration_number, password]):
        return False, "All fields are required."
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (full_name, email, institution, registration_number, password_hash, verification_status, trial_used) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (full_name.strip(), email.strip().lower(), institution.strip(), registration_number.strip(),
             hash_password(password), "Pending", 0)
        )
        conn.commit()
        return True, "Account created successfully. You may now log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()


def _row_to_user_dict(row):
    return {
        "id": row[0], "full_name": row[1], "email": row[2],
        "institution": row[3], "registration_number": row[4],
        "verification_status": row[6], "trial_used": bool(row[7]),
    }


def login(email, password):
    """Attempt to log in. Returns (success: bool, user_dict_or_message)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, full_name, email, institution, registration_number, password_hash, verification_status, trial_used "
        "FROM users WHERE email = ?",
        (email.strip().lower(),)
    )
    row = c.fetchone()
    conn.close()

    if row is None:
        return False, "No account found with this email."
    if row[5] != hash_password(password):
        return False, "Incorrect password."
    if row[6] == "Rejected":
        return False, "This account has been rejected and cannot log in. Contact the research team if you believe this is an error."

    return True, _row_to_user_dict(row)


def refresh_current_user():
    """Re-fetch the logged-in user's record from the database, so admin
    changes (verification/rejection) take effect on the next page load
    without requiring a fresh login. Forces logout if since rejected."""
    user = st.session_state.get("user")
    if user is None:
        return None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, full_name, email, institution, registration_number, password_hash, verification_status, trial_used "
        "FROM users WHERE id = ?",
        (user["id"],)
    )
    row = c.fetchone()
    conn.close()

    if row is None:
        st.session_state["user"] = None
        return None

    fresh_user = _row_to_user_dict(row)

    if fresh_user["verification_status"] == "Rejected":
        st.session_state["user"] = None
        return None

    st.session_state["user"] = fresh_user
    return fresh_user


def mark_trial_used(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET trial_used = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    if st.session_state.get("user") and st.session_state["user"]["id"] == user_id:
        st.session_state["user"]["trial_used"] = True


def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def current_user():
    return st.session_state.get("user")


def logout():
    st.session_state["user"] = None


def _render_gate_card(icon, title, sub, link_label="🔑 Go to Login / Sign Up"):
    st.markdown(
        f"""
        <div class="login-required-card">
            <div class="login-required-icon">{icon}</div>
            <div class="login-required-title">{title}</div>
            <div class="login-required-sub">{sub}</div>
            <a href="/Login" target="_self" class="gate-btn">
                {link_label}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


def require_login():
    """
    Gate for the two Predict pages:
    - Not logged in -> login prompt.
    - Rejected (detected via refresh) -> forced logout, rejection message.
    - Verified -> unlimited access.
    - Pending, trial not yet used -> allow this one time, with a notice.
    - Pending, trial already used -> blocked until verified.
    """
    if not is_logged_in():
        _render_gate_card(
            "🔒", "Login Required",
            "Please log in or create a free account to use the prediction tool."
        )

    user = refresh_current_user()

    if user is None:
        _render_gate_card(
            "⛔", "Account Rejected",
            "Your account did not pass verification and has been logged out. "
            "Contact the research team if you believe this is an error.",
            link_label="Back to Login"
        )

    if user["verification_status"] == "Verified":
        return True

    if user["trial_used"]:
        _render_gate_card(
            "🕐", "Free Trial Used",
            "You've already used your one free trial prediction. Further use "
            "unlocks once your account is verified by the research team.",
            link_label="← Back to Account"
        )

    st.info(
        "🎁 **Free trial**: your account is pending verification. You can use "
        "the prediction tool **once** before verification completes — this "
        "attempt will use your free trial."
    )
    return True


def get_all_users():
    """Return all registered users as a list of dicts, for the admin review page."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, full_name, email, institution, registration_number, verification_status, created_at, trial_used "
        "FROM users ORDER BY created_at DESC"
    )
    rows = c.fetchall()
    conn.close()

    return [
        {
            "id": r[0], "full_name": r[1], "email": r[2], "institution": r[3],
            "registration_number": r[4], "verification_status": r[5], "created_at": r[6],
            "trial_used": bool(r[7]),
        }
        for r in rows
    ]


def update_verification_status(user_id: int, new_status: str):
    """Set a user's verification_status to 'Verified', 'Pending', or 'Rejected'."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET verification_status = ? WHERE id = ?", (new_status, user_id))
    conn.commit()
    conn.close()