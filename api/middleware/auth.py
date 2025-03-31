from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User
from models.api_key import ApiKey
import datetime

def jwt_required_with_api_key(fn):
    """
    Custom decorator that allows authentication with either JWT or API Key
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Check for JWT first
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except:
            # If JWT fails, check for API key
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({"message": "Missing authentication token or API key"}), 401
            
            # Verify API key
            key_hash = hash_api_key(api_key)
            api_key_record = ApiKey.query.filter_by(key_hash=key_hash).first()
            
            if not api_key_record or not api_key_record.is_active:
                return jsonify({"message": "Invalid API key"}), 401
            
            # Check if expired
            if api_key_record.expires_at < datetime.datetime.utcnow():
                return jsonify({"message": "API key has expired"}), 401
            
            # Set the identity to the user associated with this key
            user = User.query.get(api_key_record.user_id)
            if not user or not user.is_active:
                return jsonify({"message": "User account is inactive or not found"}), 401
            
            # Manual setup of the identity
            _current_user = user.id
            
            return fn(*args, **kwargs)
    
    return wrapper

def admin_required(fn):
    """
    Decorator to check if the current user is an admin
    Must be used after jwt_required or jwt_required_with_api_key
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({"message": "Admin privileges required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper

def hash_api_key(api_key):
    """Simple hash function for API keys"""
    # In a real application, use a more secure hashing algorithm
    # This is just a placeholder
    import hashlib
    return hashlib.sha256(api_key.encode()).hexdigest()