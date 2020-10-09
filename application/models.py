from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Users(db.Model, UserMixin):
    __tablename__ = 'users_db'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    passwd_hash = db.Column(db.String(128))
    invitation_code = db.Column(db.String(64), unique=True)

    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.String(128))
    login_attempts = db.Column(db.Integer)

    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    account_confirmed = db.Column(db.Boolean(), default=False)
    confirmed_on = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship to invitations table
    created_invitations = db.relationship('Invitations', backref='creator')
    # relationship to the Posts table
    created_posts = db.relationship('Posts', backref='creator')


    def __repr__(self):
        return f"<Member username {self.username}"

    def set_password(self, password):
        self.passwd_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwd_hash, password)

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


#for storing invitation codes
class Invitations(db.Model, UserMixin):
    __tablename__ = 'invitation_codes'
    id = db.Column(db.Integer, primary_key=True)
    invitation_code = db.Column(db.String(64), unique=True)
    expired = db.Column(db.Boolean(), default=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users_db.id'))

    def __repr__(self):
        return f"{self.invitation_code}"


class Posts(db.Model):
    __tablename__ = 'users_posts'
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(128))
    post_thumbnail = db.Column(db.LargeBinary)
    thumbnail_name = db.Column(db.String(256))
    post_text = db.Column(db.Text)
    post_url = db.Column(db.String(512), unique=True)
    creation_date = db.Column(db.String(256))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    post_author = db.Column(db.String(128))
    post_about = db.Column(db.String(32))

    creator_id = db.Column(db.Integer, db.ForeignKey('users_db.id'))

    def __repr__(self):
        return f"{self.post_url}"


