import os
from datetime import timedelta

# Database
DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql://postgres:postgres@localhost:5432/vulcnn')
SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT Config
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Upload Config
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '../data/uploads')
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload

# Service URLs
NORMALIZATION_SERVICE_URL = os.environ.get('NORMALIZATION_SERVICE_URL', 'http://normalization:5001')
PDG_GENERATOR_SERVICE_URL = os.environ.get('PDG_GENERATOR_SERVICE_URL', 'http://pdg-generator:5002')
IMAGE_GENERATOR_SERVICE_URL = os.environ.get('IMAGE_GENERATOR_SERVICE_URL', 'http://image-generator:5003')
PREDICTION_SERVICE_URL = os.environ.get('PREDICTION_SERVICE_URL', 'http://prediction:5004')
RESULTS_SERVICE_URL = os.environ.get('RESULTS_SERVICE_URL', 'http://results:5005')