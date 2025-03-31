from app import db

class PDG(db.Model):
    __tablename__ = 'pdgs'

    id = db.Column(db.String(36), primary_key=True)
    file_id = db.Column(db.String(36), db.ForeignKey('files.id'), nullable=False)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id'), nullable=False)
    pdg_data = db.Column(db.Text)  # DOT format or other serialized format
    image_data = db.Column(db.Text)  # Serialized image representation

    def __init__(self, id, file_id, scan_id, pdg_data, image_data=None):
        self.id = id
        self.file_id = file_id
        self.scan_id = scan_id
        self.pdg_data = pdg_data
        self.image_data = image_data

    def to_dict(self):
        return {
            'id': self.id,
            'file_id': self.file_id,
            'scan_id': self.scan_id,
            'pdg_data': self.pdg_data,
            'image_data': self.image_data
        }