from app import db
from datetime import datetime

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.String(36), primary_key=True)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='uploaded')

    # Relationships
    vulnerabilities = db.relationship('Vulnerability', backref='file', lazy=True)
    pdgs = db.relationship('PDG', backref='file', lazy=True)

    def __init__(self, id, project_id, filename, file_path, content_type, file_size):
        self.id = id
        self.project_id = project_id
        self.filename = filename
        self.file_path = file_path
        self.content_type = content_type
        self.file_size = file_size

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'content_type': self.content_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat(),
            'status': self.status
        }