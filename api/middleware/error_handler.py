from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'message': 'Bad request',
            'error': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'message': 'Unauthorized',
            'error': str(error)
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'message': 'Forbidden',
            'error': str(error)
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'message': 'Resource not found',
            'error': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'message': 'Internal server error',
            'error': str(error)
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Handle all HTTP exceptions"""
        response = e.get_response()
        response.data = jsonify({
            'message': e.description,
            'error': e.name,
            'code': e.code
        }).data
        response.content_type = "application/json"
        return response
    
    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Handle all unhandled exceptions"""
        app.logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500