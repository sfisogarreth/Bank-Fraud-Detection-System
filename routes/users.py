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
    generate_password_hash
)

from database.connection import (
    get_db_connection
)

from services.security import (
    login_required,
    role_required
)

users_bp = Blueprint(
    "users",
    __name__
)


# ==================================================
# AUDIT LOG
# ==================================================

def log_audit(user_id, action):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO audit_logs
            (
                user_id,
                action
            )
            VALUES (?, ?)
            """,
            (
                user_id,
                action
            )
        )

        conn.commit()

    finally:

        cursor.close()
        conn.close()


# ==================================================
# USER LIST
# ==================================================

@users_bp.route("/")
@login_required
@role_required("Admin")
def users():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            email,
            role,
            failed_attempts,
            account_locked,
            last_login,
            created_at
        FROM users
        ORDER BY created_at DESC
    """)

    users_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "users.html",
        users=users_list
    )


# ==================================================
# CREATE USER
# ==================================================

@users_bp.route(
    "/create",
    methods=["POST"]
)
@login_required
@role_required("Admin")
def create_user():

    username = request.form.get(
        "username",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    role = request.form.get(
        "role",
        "Customer"
    )

    if not username or not email or not password:

        flash(
            "All fields are required.",
            "error"
        )

        return redirect(
            url_for("users.users")
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        hashed_password = generate_password_hash(
            password
        )

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password_hash,
                role
            )
            VALUES
            (?, ?, ?, ?)
            """,
            (
                username,
                email,
                hashed_password,
                role
            )
        )

        conn.commit()

        log_audit(
            session.get("user_id"),
            f"Created User: {username}"
        )

        flash(
            "User created successfully.",
            "success"
        )

    except Exception:

        conn.rollback()

        flash(
            "User already exists.",
            "error"
        )

    finally:

        cursor.close()
        conn.close()

    return redirect(
        url_for("users.users")
    )


# ==================================================
# LOCK USER
# ==================================================

@users_bp.route(
    "/lock/<int:user_id>"
)
@login_required
@role_required("Admin")
def lock_user(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET account_locked = 1
        WHERE id = ?
        """,
        (user_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    log_audit(
        session.get("user_id"),
        f"Locked User ID {user_id}"
    )

    flash(
        "User locked.",
        "success"
    )

    return redirect(
        url_for("users.users")
    )


# ==================================================
# UNLOCK USER
# ==================================================

@users_bp.route(
    "/unlock/<int:user_id>"
)
@login_required
@role_required("Admin")
def unlock_user(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET
            account_locked = 0,
            failed_attempts = 0
        WHERE id = ?
        """,
        (user_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    log_audit(
        session.get("user_id"),
        f"Unlocked User ID {user_id}"
    )

    flash(
        "User unlocked.",
        "success"
    )

    return redirect(
        url_for("users.users")
    )