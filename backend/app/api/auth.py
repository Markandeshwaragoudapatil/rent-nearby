import re
from flask import Blueprint, abort, g, jsonify, request, session
from sqlalchemy import func, select
from flask_wtf.csrf import generate_csrf
from ..extensions import db, limiter
from ..models import User
from ..security import hash_password, login_required, verify_password

auth_bp = Blueprint("auth", __name__)

def payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="A JSON object is required.")
    return data

@auth_bp.get("/csrf")
def csrf():
    return jsonify({"csrf_token": generate_csrf()})

@auth_bp.post("/register")
@limiter.limit("5 per hour")
def register():
    data = payload()
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    if not name or len(name) > 100:
        abort(422, description="Name is required and must be at most 100 characters.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(email) > 255:
        abort(422, description="Enter a valid email address.")
    if db.session.scalar(select(User.id).where(func.lower(User.email) == email)):
        abort(409, description="An account with this email already exists.")
    try:
        encoded = hash_password(password)
    except ValueError as error:
        abort(422, description=str(error))
    user = User(name=name, email=email, password_hash=encoded, role="RENTER")
    db.session.add(user)
    db.session.commit()
    session.clear()
    session["user_id"] = str(user.id)
    session.permanent = True
    return jsonify({"user": user.to_dict()}), 201

@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = payload()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    user = db.session.scalar(select(User).where(func.lower(User.email) == email))
    if user is None or not user.is_active or not verify_password(user.password_hash, password):
        abort(401, description="Invalid email or password.")
    session.clear()
    session["user_id"] = str(user.id)
    session.permanent = True
    return jsonify({"user": user.to_dict()})

@auth_bp.post("/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})

@auth_bp.get("/me")
@login_required
def me():
    return jsonify({"user": g.current_user.to_dict()})
