from flask import Flask
from flask_apscheduler import APScheduler

import os
import datetime

from .blueprint.home.routes import home_bp, joke
from .blueprint.facebook.routes import facebook_bp, downloadFaces
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

    sched = APScheduler()
    sched.init_app(app)
    sched.start()

    with app.app_context() :
        from .models import db
        db.init_app(app)
        db.create_all()

        app.apscheduler.add_job(func=scheduler1, trigger="interval", args=[app], seconds=300, id="download_job_id", next_run_time=datetime.datetime.now())

        return app

def scheduler1(a) :
    print("STARTING SCHEDULE TASK")
    with a.app_context() :
        res = downloadFaces()
        print(res)