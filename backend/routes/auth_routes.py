from flask import Blueprint, jsonify, request

from backend.extensions import db
from backend.models import User
from backend.services.auth_service import (
    get_current_user,
    login_required,
    login_user,
    logout_user,
)
from backend.services.monitoring_service import log_system_event


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required"}), 400

    import re
    if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[A-Z]", password) or not re.search(r"[@.$!%*?&#_]", password):
        return jsonify({"success": False, "message": "Password must be at least 8 characters long, contain a number, an uppercase letter, and a special character"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered"}), 409

    user = User(name=name, email=email, role="recruiter", status="active")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    log_system_event("INFO", "auth", f"Recruiter registered: {email}")
    return jsonify({"success": True, "message": "Registration successful", "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        log_system_event("WARNING", "auth", f"Failed login attempt for {email or 'unknown'}")
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    if user.status != "active":
        return jsonify({"success": False, "message": "Account is inactive"}), 403

    login_user(user)
    log_system_event("INFO", "auth", f"Successful login for {email}")
    return jsonify({"success": True, "message": "Login successful", "user": user.to_dict()})


@auth_bp.post("/logout")
@login_required
def logout():
    user = get_current_user()
    if user:
        log_system_event("INFO", "auth", f"User logged out: {user.email}")
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})


@auth_bp.get("/me")
@login_required
def me():
    user = get_current_user()
    return jsonify({"success": True, "user": user.to_dict()})


@auth_bp.put("/profile")
@login_required
def update_profile():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    password = data.get("password") or ""
    current_password = data.get("current_password") or ""

    if name:
        user.name = name
    if password:
        if not user.check_password(current_password):
            return jsonify({"success": False, "message": "Current password is required to set a new password"}), 400
        
        import re
        if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[A-Z]", password) or not re.search(r"[@.$!%*?&#_]", password):
            return jsonify({"success": False, "message": "Password must be at least 8 characters long, contain a number, an uppercase letter, and a special character"}), 400
        user.set_password(password)

    db.session.commit()
    return jsonify({"success": True, "message": "Profile updated", "user": user.to_dict()})
