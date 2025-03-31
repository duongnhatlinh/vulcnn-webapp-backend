from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC))
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    projects = db.relationship('Project', backref='user', lazy=True)
    scans = db.relationship('Scan', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)
    api_keys = db.relationship('ApiKey', backref='user', lazy=True)
    webhooks = db.relationship('Webhook', backref='user', lazy=True)

    def __init__(self, id, email, password, name, role='user'):
        self.id = id
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }