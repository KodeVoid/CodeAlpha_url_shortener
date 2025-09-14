from flask import jsonify

def register_error_handlers(app):
    """Register JSON error handlers with the Flask app."""

    def _json_error(status_code: int, error: str, message: str):
        response = jsonify({
            "error": error,
            "message": message
        })
        response.status_code = status_code
        return response

    @app.errorhandler(400)
    def bad_request(e):
        return _json_error(400, "BadRequest", "The request could not be understood or was missing required parameters.")

    @app.errorhandler(401)
    def unauthorized(e):
        return _json_error(401, "Unauthorized", "Authentication is required to access this resource.")

    @app.errorhandler(403)
    def forbidden(e):
        return _json_error(403, "Forbidden", "You do not have permission to access this resource.")

    @app.errorhandler(404)
    def not_found(e):
        return _json_error(404, "NotFound", "The requested resource was not found.")

    @app.errorhandler(405)
    def method_not_allowed(e):
        return _json_error(405, "MethodNotAllowed", "The HTTP method used is not allowed for this endpoint.")

    @app.errorhandler(500)
    def internal_server_error(e):
        return _json_error(500, "InternalServerError", "An unexpected error occurred on the server.")

    # Catch-all for any unhandled exceptions
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}")
        return _json_error(500, "UnexpectedError", "An unexpected error occurred. Please try again later.")
