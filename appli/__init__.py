from flask import Flask

import os

from .blueprint.home.routes import home_bp
from .blueprint.facebook.routes import facebook_bp
from .blueprint.admin.routes import admin_bp

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_FACEBOOK_FACES')
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/facebook_faces'
    app.secret_key = os.environ.get('SECRET_KEY_FBFACE')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.register_blueprint(home_bp)
    app.register_blueprint(facebook_bp)
    app.register_blueprint(admin_bp)

    with app.app_context() :
        from .models import db
        db.init_app(app)
        db.create_all()

        return app