from functools import wraps
from flask import (
    session,
    flash,
    redirect,
    url_for,
    request
)


# --------------------------------------------------
# LOGIN REQUIRED
# --------------------------------------------------

def login_required(func):
    """
    User must be logged in.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        return func(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# ROLE CHECK
# --------------------------------------------------

def role_required(*roles):
    """
    Restrict endpoint access
    to specific roles.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            user_role = session.get("role")

            if user_role not in roles:

                flash(
                    "Access denied.",
                    "danger"
                )

                return redirect(
                    url_for("dashboard.dashboard")
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


# --------------------------------------------------
# ROLE HELPERS
# --------------------------------------------------

def is_admin():
    return session.get("role") == "Admin"


def is_manager():
    return session.get("role") == "Manager"


def is_customer():
    return session.get("role") == "Customer"


# --------------------------------------------------
# CURRENT USER HELPERS
# --------------------------------------------------

def current_user_id():
    return session.get("user_id")


def current_username():
    return session.get("username")


def current_role():
    return session.get("role")


# --------------------------------------------------
# PERMISSION CHECKS
# --------------------------------------------------

def can_manage_users():
    return session.get("role") == "Admin"


def can_view_reports():
    return session.get("role") in [
        "Admin",
        "Manager"
    ]


def can_access_investigations():
    return session.get("role") in [
        "Admin",
        "Manager"
    ]


def can_access_settings():
    return session.get("role") == "Admin"


def can_access_backups():
    return session.get("role") == "Admin"


# --------------------------------------------------
# DASHBOARD REDIRECT
# --------------------------------------------------

def role_dashboard():

    role = session.get("role")

    if role == "Admin":
        return "Administrator"

    if role == "Manager":
        return "Manager"

    return "Customer"