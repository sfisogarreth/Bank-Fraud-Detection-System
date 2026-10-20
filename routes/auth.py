import time
import re
from collections import defaultdict
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.connection import get_db_connection

auth_bp = Blueprint('auth', __name__)

# --------------------------------------------------
# In-memory IP rate limiter
# --------------------------------------------------

_login_attempts = defaultdict(list)

def _check_rate_limit(ip, max_attempts=5, window=300):
    """
    Block IP after too many failed requests
    within a time window.
    """
    now = time.time()

    _login_attempts[ip] = [
        t for t in _login_attempts[ip]
        if now - t < window
    ]

    if len(_login_attempts[ip]) >= max_attempts:
        return False

    _login_attempts[ip].append(now)
    return True


# --------------------------------------------------
# Password Validation
# --------------------------------------------------

def _validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter."

    if not re.search(r"\d", password):
        return False, "Password must contain a number."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain a special character."

    return True, ""


# --------------------------------------------------
# Audit Logging Helper
# --------------------------------------------------

def log_audit(user_id, action, transaction_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO audit_logs
            (user_id, action, transaction_id)
            VALUES (?, ?, ?)
            """,
            (user_id, action, transaction_id)
        )

        conn.commit()

    except Exception:
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get(
            'username',
            ''
        ).strip()

        email = request.form.get(
            'email',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        if not username or not email or not password:
            flash(
                "All fields are required.",
                "error"
            )
            return redirect(url_for('auth.signup'))

        if not re.match(
            r'^[\w\.-]+@[\w\.-]+\.\w+$',
            email
        ):
            flash(
                "Invalid email address.",
                "error"
            )
            return redirect(url_for('auth.signup'))

        strong, message = _validate_password(password)

        if not strong:
            flash(message, "error")
            return redirect(url_for('auth.signup'))

        hashed_pw = generate_password_hash(
            password,
            method='pbkdf2:sha256'
        )

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users
                (
                    username,
                    email,
                    password_hash,
                    role
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    username,
                    email,
                    hashed_pw,
                    "Customer"
                )
            )

            user_id = cursor.lastrowid

            conn.commit()

            log_audit(
                user_id,
                "User Registration"
            )

            flash(
                "Account created successfully. Please login.",
                "success"
            )

            return redirect(
                url_for('auth.login')
            )

        except Exception:
            conn.rollback()

            flash(
                "Username or email already exists.",
                "error"
            )

        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get(
            'email',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        if not email or not password:
            flash(
                "Please enter email and password.",
                "error"
            )
            return redirect(
                url_for('auth.login')
            )

        if not _check_rate_limit(
            request.remote_addr
        ):
            flash(
                "Too many login attempts. Try again later.",
                "error"
            )
            return render_template(
                "login.html"
            ), 429

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                username,
                email,
                password_hash,
                role,
                failed_attempts,
                account_locked
            FROM users
            WHERE email = ?
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        if user["account_locked"]:
            cursor.close()
            conn.close()

            flash(
                "Account locked. Contact administrator.",
                "error"
            )

            return render_template(
                "login.html"
            )

        if check_password_hash(
            user["password_hash"],
            password
        ):
            cursor.execute(
                """
                UPDATE users
                SET
                    failed_attempts = 0,
                    last_login = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (user["id"],)
            )

            conn.commit()

            session.clear()

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            log_audit(
                user["id"],
                "Login"
            )

            cursor.close()
            conn.close()

            flash(
                f"Welcome back {user['username']}!",
                "success"
            )

            return redirect(
                url_for("dashboard.dashboard")
            )

        else:
            attempts = user["failed_attempts"] + 1

            if attempts >= 5:
                cursor.execute(
                    """
                    UPDATE users
                    SET
                        failed_attempts = ?,
                        account_locked = 1
                    WHERE id = ?
                    """,
                    (
                        attempts,
                        user["id"]
                    )
                )

                flash(
                    "Account locked after 5 failed attempts.",
                    "error"
                )

            else:
                cursor.execute(
                    """
                    UPDATE users
                    SET failed_attempts = ?
                    WHERE id = ?
                    """,
                    (
                        attempts,
                        user["id"]
                    )
                )

                remaining = 5 - attempts

                flash(
                    f"Invalid password. {remaining} attempt(s) remaining.",
                    "error"
                )

            conn.commit()

            cursor.close()
            conn.close()

    return render_template(
        "login.html"
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@auth_bp.route('/logout')
def logout():
    user_id = session.get(
        "user_id"
    )

    if user_id:
        log_audit(
            user_id,
            "Logout"
        )

    session.clear()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for('auth.login')
    )