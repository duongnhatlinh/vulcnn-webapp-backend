from app import db
from datetime import datetime, timedelta
import uuid

class ApiKey(db.Model):
    __tablename__ = 'api_keys'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    key_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, id, user_id, key_hash, name, expires_at=None):
        self.id = id
        self.user_id = user_id
        self.key_hash = key_hash
        self.name = name
        if expires_at:
            self.expires_at = expires_at
        else:
            # Default expiration: 1 year
            self.expires_at = datetime.utcnow() + timedelta(days=365)

    def is_expired(self):
        return self.expires_at < datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active
        }