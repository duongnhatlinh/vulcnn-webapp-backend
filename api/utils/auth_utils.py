import hashlib
import secrets
import jwt
import time
from functools import wraps
from flask import request, current_app, jsonify

def generate_password_salt():
    """
    Generate a random salt for password hashing
    
    Returns:
        str: Random salt string
    """
    return secrets.token_hex(16)

def hash_password(password, salt):
    """
    Hash a password with a salt
    
    Args:
        password (str): Password to hash
        salt (str): Salt to use
        
    Returns:
        str: Hashed password
    """
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()

def verify_password(stored_password, provided_password, salt):
    """
    Verify a password against a stored hash
    
    Args:
        stored_password (str): Stored password hash
        provided_password (str): Password to verify
        salt (str): Salt used for hashing
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return stored_password == hash_password(provided_password, salt)

def hash_api_key(api_key):
    """
    Hash an API key for storage
    
    Args:
        api_key (str): API key to hash
        
    Returns:
        str: Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()

def generate_webhook_signature(payload, secret):
    """
    Generate a signature for a webhook payload
    
    Args:
        payload (dict): Webhook payload
        secret (str): Webhook secret
        
    Returns:
        str: Signature
    """
    payload_str = json.dumps(payload, sort_keys=True)
    return hmac.new(
        secret.encode('utf-8'),
        payload_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def verify_webhook_signature(signature, payload, secret):
    """
    Verify a webhook signature
    
    Args:
        signature (str): Signature to verify
        payload (dict): Webhook payload
        secret (str): Webhook secret
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    expected_signature = generate_webhook_signature(payload, secret)
    return hmac.compare_digest(signature, expected_signature)