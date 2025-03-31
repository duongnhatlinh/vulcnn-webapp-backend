from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Khởi tạo Flask app
app = Flask(__name__)
app.config.from_object('config')

# Khởi tạo CORS
CORS(app)

# Khởi tạo các extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
api = Api(app)

# Import controllers
from controllers.auth import auth_bp
from controllers.projects import projects_bp
from controllers.files import files_bp
from controllers.scans import scans_bp
from controllers.reports import reports_bp

# Import middleware
from middleware.error_handler import register_error_handlers

# Đăng ký các routes
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(projects_bp, url_prefix='/api/projects')
app.register_blueprint(files_bp, url_prefix='/api/files')
app.register_blueprint(scans_bp, url_prefix='/api/scans')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# Đăng ký error handlers
register_error_handlers(app)

# Initialize models (to avoid circular imports)
import models.user
import models.project
import models.file
import models.scan
import models.vulnerability
import models.pdg
import models.report
import models.api_key
import models.webhook

@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'ok', 'version': '1.0.0'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')