from app import db
from datetime import datetime
import json

class Webhook(db.Model):
    __tablename__ = 'webhooks'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    secret_hash = db.Column(db.String(255))
    events = db.Column(db.Text)  # JSON array of event types
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, id, user_id, url, secret_hash=None, events=None):
        self.id = id
        self.user_id = user_id
        self.url = url
        self.secret_hash = secret_hash
        if events:
            self.events = json.dumps(events)

    def get_events(self):
        if self.events:
            return json.loads(self.events)
        return []

    def set_events(self, events):
        self.events = json.dumps(events)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'url': self.url,
            'events': self.get_events(),
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }