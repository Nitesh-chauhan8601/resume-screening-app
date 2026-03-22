from functools import wraps

from flask import jsonify, session

from backend.models import User


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_user(user: User) -> None:
    session["user_id"] = user.id
    session["user_role"] = user.role


def logout_user() -> None:
    session.clear()


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return view_func(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"success": False, "message": "Authentication required"}), 401
            if user.role not in roles:
                return jsonify({"success": False, "message": "Access denied"}), 403
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
