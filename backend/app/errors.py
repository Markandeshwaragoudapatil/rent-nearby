from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http(error):
        return jsonify({"error": {"code": error.name.upper().replace(" ", "_"), "message": error.description}}), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        app.logger.exception("Unhandled request error")
        return jsonify({"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}}), 500
