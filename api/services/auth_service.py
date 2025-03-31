import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
import hashlib
import secrets

from app import db
from models.user import User
from models.api_key import ApiKey

def register_user(email, password, name, role='user'):
    """
    Register a new user
    
    Args:
        email (str): User email
        password (str): User password
        name (str): User name
        role (str): User role (default: 'user')
        
    Returns:
        tuple: (user, access_token, refresh_token)
    """
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Create new user
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=email,
        password=password,
        name=name,
        role=role
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    
    return new_user, access_token, refresh_token

def authenticate_user(email, password):
    """
    Authenticate a user with email and password
    
    Args:
        email (str): User email
        password (str): User password
        
    Returns:
        tuple: (user, access_token, refresh_token)
    """
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        raise ValueError("Invalid email or password")
    
    if not user.is_active:
        raise ValueError("Account is deactivated")
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return user, access_token, refresh_token

def get_user_by_id(user_id):
    """
    Get a user by ID
    
    Args:
        user_id (str): User ID
        
    Returns:
        User: User object
    """
    user = User.query.get(user_id)
    
    if not user:
        raise ValueError("User not found")
    
    return user

def change_user_password(user_id, current_password, new_password):
    """
    Change a user's password
    
    Args:
        user_id (str): User ID
        current_password (str): Current password
        new_password (str): New password
        
    Returns:
        User: Updated user object
    """
    user = User.query.get(user_id)
    
    if not user:
        raise ValueError("User not found")
    
    # Verify current password
    if not user.check_password(current_password):
        raise ValueError("Current password is incorrect")
    
    # Update password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    return user

def generate_api_key(user_id, name, expiration_days=365):
    """
    Generate a new API key for a user
    
    Args:
        user_id (str): User ID
        name (str): Key name
        expiration_days (int): Expiration in days
        
    Returns:
        tuple: (api_key_string, api_key_object)
    """
    user = User.query.get(user_id)
    
    if not user:
        raise ValueError("User not found")
    
    # Generate a secure random API key
    api_key_string = secrets.token_urlsafe(32)
    
    # Hash the API key for storage
    key_hash = hashlib.sha256(api_key_string.encode()).hexdigest()
    
    # Calculate expiration date
    expires_at = datetime.utcnow() + timedelta(days=expiration_days)
    
    # Create API key record
    api_key_id = str(uuid.uuid4())
    api_key = ApiKey(
        id=api_key_id,
        user_id=user_id,
        key_hash=key_hash,
        name=name,
        expires_at=expires_at
    )
    
    db.session.add(api_key)
    db.session.commit()
    
    return api_key_string, api_key

def revoke_api_key(api_key_id, user_id):
    """
    Revoke an API key
    
    Args:
        api_key_id (str): API key ID
        user_id (str): User ID
        
    Returns:
        ApiKey: Updated API key object
    """
    api_key = ApiKey.query.filter_by(id=api_key_id, user_id=user_id).first()
    
    if not api_key:
        raise ValueError("API key not found")
    
    api_key.is_active = False
    db.session.commit()
    
    return api_key