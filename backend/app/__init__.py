import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import DevelopmentConfig, ProductionConfig
from .extensions import csrf, db, limiter, migrate

def create_app(config_object=None):
    app = Flask(__name__)
    if config_object is None:
        if os.getenv("FLASK_ENV") == "production":
            if not os.getenv("SECRET_KEY"):
                raise RuntimeError("SECRET_KEY must be set in production.")
            if os.getenv("RATELIMIT_STORAGE_URI", "memory://").startswith("memory://"):
                raise RuntimeError("Configure a persistent rate-limit store in production.")
            config_object = ProductionConfig
        else:
            config_object = DevelopmentConfig
    app.config.from_object(config_object)
    db.init_app(app)
    migrate.init_app(app, directory=os.path.join(os.path.dirname(__file__), "..", "migrations"))
    csrf.init_app(app)
    limiter.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True,
         allow_headers=["Content-Type", "X-CSRFToken", "Idempotency-Key"],
         methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"])
    from . import models
    from .api import register_blueprints
    from .errors import register_error_handlers
    register_blueprints(app)

    @app.get("/")
    def index():
        return jsonify({"name": "RentNearby API", "version": "1.0", "status": "ok"})
    return app
