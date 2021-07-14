from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

# Create database connection object
db = SQLAlchemy()

class Image(db.Model) :
    __tablename__ = "image"
    img_id = db.Column(db.Integer, primary_key=True)
    img_fb_id = db.Column(db.String(50))
    img_url = db.Column(db.Text)
    img_filename = db.Column(db.Text)
    img_alt = db.Column(db.Text)
    img_has_face = db.Column(db.Boolean)
    img_encoding = db.Column(db.Text)
    img_date_creation = db.Column(db.DateTime)
    img_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    img_user = db.relationship('User', back_populates="user_images")

class User(db.Model) :
    __tablename__ ="user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_fb_id = db.Column(db.String(100))
    user_fb_name = db.Column(db.String(100))
    user_friends = db.Column(db.Text)
    user_retrieved_friends = db.Column(db.Boolean)
    user_retrieved_pictures = db.Column(db.Boolean)
    user_date_creation = db.Column(db.DateTime)
    user_date_retrieved_friends = db.Column(db.DateTime)
    user_date_retrieved_pictures = db.Column(db.DateTime)
    user_images = db.relationship("Image", back_populates="img_user")

class Upload(db.Model) :
    __tablename__ = "upload"
    up_id = db.Column(db.Integer, primary_key=True)
    up_filename = db.Column(db.Text)
    up_original_name = db.Column(db.Text)
    up_has_face = db.Column(db.Boolean)
    up_encoding = db.Column(db.Text)
    up_date_creation = db.Column(db.DateTime)
    up_ip_adress = db.Column(db.String(25))
    up_user_agent = db.Column(db.Text)

class Account(db.Model) :
    __tablename__ = "account"
    account_id = db.Column(db.Integer, primary_key=True)
    account_email = db.Column(db.Text)
    account_password = db.Column(db.Text)
    account_nb_use = db.Column(db.Integer)
    account_date_last_use = db.Column(db.DateTime)
    account_active = db.Column(db.Boolean)
    account_nb_problem = db.Column(db.Integer)
    account_problem_info = db.Column(db.Text)


def insert_first_data():
    accounts_data = [
        ("charles.razaraza@gmail.com", "KarinRamiliarisoa"),
        ("tom.rasirasi@gmail.com", "CharlesRazanakoto"),
        ("lunerougeflunflik@gmail.com", "Bloodlad666"),
    ]

    for acc in accounts_data :
        account = Account()
        account.account_email = acc[0]
        account.account_password = acc[1]
        account.account_nb_use = 0
        account.account_active = True
        account.account_nb_problem = 0

        db.session.add(account)
        db.session.commit()