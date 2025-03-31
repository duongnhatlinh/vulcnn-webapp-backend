from app import db
from datetime import datetime
import json

class Scan(db.Model):
    __tablename__ = 'scans'

    id = db.Column(db.String(36), primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='pending')
    scan_options = db.Column(db.Text)  # JSON string
    vulnerabilities_count = db.Column(db.Integer, default=0)
    high_severity_count = db.Column(db.Integer, default=0)
    medium_severity_count = db.Column(db.Integer, default=0)
    low_severity_count = db.Column(db.Integer, default=0)

    # Relationships
    vulnerabilities = db.relationship('Vulnerability', backref='scan', lazy=True)
    pdgs = db.relationship('PDG', backref='scan', lazy=True)
    reports = db.relationship('Report', backref='scan', lazy=True)

    def __init__(self, id, project_id, user_id, scan_options=None):
        self.id = id
        self.project_id = project_id
        self.user_id = user_id
        if scan_options:
            self.scan_options = json.dumps(scan_options)

    def get_scan_options(self):
        if self.scan_options:
            return json.loads(self.scan_options)
        return {}

    def set_scan_options(self, options):
        self.scan_options = json.dumps(options)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'scan_options': self.get_scan_options(),
            'vulnerabilities_count': self.vulnerabilities_count,
            'high_severity_count': self.high_severity_count,
            'medium_severity_count': self.medium_severity_count,
            'low_severity_count': self.low_severity_count
        }