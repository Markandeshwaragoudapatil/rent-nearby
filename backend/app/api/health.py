from flask import Blueprint, current_app, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "database": "ok"})
    except SQLAlchemyError:
        current_app.logger.exception("Database health check failed")
        return jsonify({"status": "degraded", "database": "unavailable"}), 503
