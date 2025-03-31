from app import db
from datetime import datetime
import json

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.String(36), primary_key=True)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # pdf, csv, html, etc.
    file_path = db.Column(db.String(512), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    report_options = db.Column(db.Text)  # JSON string

    def __init__(self, id, scan_id, user_id, report_type, file_path, report_options=None):
        self.id = id
        self.scan_id = scan_id
        self.user_id = user_id
        self.report_type = report_type
        self.file_path = file_path
        if report_options:
            self.report_options = json.dumps(report_options)

    def get_report_options(self):
        if self.report_options:
            return json.loads(self.report_options)
        return {}

    def set_report_options(self, options):
        self.report_options = json.dumps(options)

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'file_path': self.file_path,
            'generated_at': self.generated_at.isoformat(),
            'report_options': self.get_report_options()
        }