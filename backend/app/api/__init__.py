from .auth import auth_bp
from .availability import availability_bp
from .bookings import bookings_bp
from .catalog import catalog_bp
from .health import health_bp
from .owner import owner_bp

def register_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(catalog_bp, url_prefix="/api/v1")
    app.register_blueprint(owner_bp, url_prefix="/api/v1/owner")
    app.register_blueprint(bookings_bp, url_prefix="/api/v1")
    app.register_blueprint(availability_bp, url_prefix="/api/v1")
