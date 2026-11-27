from functools import wraps
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from flask import abort, g, session
from .extensions import db
from .models import User

_password_hasher = PasswordHasher()

def hash_password(password):
    if not isinstance(password, str) or len(password) < 12 or len(password) > 128:
        raise ValueError("Password must contain between 12 and 128 characters.")
    return _password_hasher.hash(password)

def verify_password(encoded, password):
    try:
        return _password_hasher.verify(encoded, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError, TypeError):
        return False

def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        return db.session.get(User, user_id)
    except (ValueError, TypeError):
        return None

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None or not user.is_active:
            abort(401, description="Authentication required.")
        g.current_user = user
        return view(*args, **kwargs)
    return wrapped

def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.current_user.role not in roles:
                abort(403, description="You do not have permission to perform this action.")
            return view(*args, **kwargs)
        return wrapped
    return decorator
