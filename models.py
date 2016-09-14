# -*- coding: utf-8 -*-
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import BaseQuery, SQLAlchemy
from flask_login import LoginManager, make_secure_token, UserMixin

db = SQLAlchemy()

login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.token_loader
def load_token(token):
    return User.query.filter_by(auth_key=token).first()

class UserQuery(BaseQuery):
    def authenticate(self, username, password):
        user = self.filter(User.username==username).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated


class User(db.Model, UserMixin):

    __tablename__ = "auth_user"
    query_class = UserQuery

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    auth_key = db.Column(db.String(32), nullable=False)
    password = db.Column("password_hash", db.String(256), nullable=False)
    password_reset_token = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True, nullable=False)
    role = db.Column("status", db.Integer, db.ForeignKey('roles.id'), nullable=False, default=3)
    created_at = db.Column(db.Integer, default=int(time()))
    updated_at = db.Column(db.Integer, default=int(time()), onupdate=int(time()))

    def __init__(self, username, password, email, role=3):
        self.username = username
        self.password = self.set_password(password)
        self.email = email
        self.role = role
        self.auth_key = self.get_auth_token()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    def get_auth_token(self):
        return make_secure_token(self.username, self.password)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(256))

    def __str__(self):
        return self.name

class UserCertification(db.Model):
    __tablename__ = "user_certs"

    nickname = db.Column(db.String(128), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    # user = db.relationship('AppUser', backref='cert')


class AppUser(db.Model):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer)
    exp = db.Column(db.Integer)
    locked = db.Column(db.Boolean)
    cert = db.relationship('UserCertification', backref='user', uselist=False)
    prop = db.relationship('UserProperty', backref='user')
    room = db.relationship('Room', backref='user', uselist=False)


class UserProperty(db.Model):
    __tablename__ = "user_property"

    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    vcy = db.Column(db.Integer)
    # user = db.relationship('AppUser', backref='prop')


class Room(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))

if __name__ == '__main__':
    pass