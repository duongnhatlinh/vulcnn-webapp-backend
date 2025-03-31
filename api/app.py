from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Khởi tạo Flask app
app = Flask(__name__)
app.config.from_object('config')

# Khởi tạo các extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
api = Api(app)

# Đăng ký các routes
# Sẽ thêm sau

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')