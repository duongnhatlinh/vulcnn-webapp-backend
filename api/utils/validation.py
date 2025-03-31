import re
from marshmallow import Schema, fields, validate, ValidationError

# Email regex pattern
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, otherwise raises ValidationError
    """
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Invalid email format")
    return True

def validate_password(password):
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
        
    Returns:
        bool: True if valid, otherwise raises ValidationError
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit")
    
    # Check for at least one letter
    if not any(char.isalpha() for char in password):
        raise ValidationError("Password must contain at least one letter")
    
    return True

class UserSchema(Schema):
    """Schema for validating user data"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True, validate=validate_email)
    password = fields.Str(required=True, validate=validate_password)

class ProjectSchema(Schema):
    """Schema for validating project data"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(validate=validate.Length(max=1000))

class ScanOptionsSchema(Schema):
    """Schema for validating scan options"""
    deepScan = fields.Bool()
    includeLibraries = fields.Bool()
    detailedReport = fields.Bool()
    pdgVisualization = fields.Bool()

def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension
    
    Args:
        filename (str): Name of the file
        allowed_extensions (list): List of allowed extensions
        
    Returns:
        bool: True if valid, otherwise raises ValidationError
    """
    ext = filename.split('.')[-1].lower()
    if f'.{ext}' not in allowed_extensions:
        raise ValidationError(f"File type .{ext} not allowed. Allowed types: {', '.join(allowed_extensions)}")
    return True