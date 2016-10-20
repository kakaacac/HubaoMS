# -*- coding: utf-8 -*-
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import BaseQuery, SQLAlchemy
from flask_login import make_secure_token, UserMixin
from sqlalchemy.dialects.postgresql import JSON, UUID


db = SQLAlchemy()

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


class AppUser(db.Model):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID)
    avatar = db.Column(db.String(256))
    sex = db.Column("other_info", JSON)
    level = db.Column(db.Integer)
    exp = db.Column(db.Integer)
    vip = db.Column(db.Boolean)
    locked = db.Column(db.Boolean)
    locked_time = db.Column(db.DateTime(timezone=False))
    display_name = db.Column(db.String(256))
    active_device = db.Column(db.Integer, db.ForeignKey('device.did'))
    cert = db.relationship('UserCertification', backref='user', uselist=False)
    prop = db.relationship('UserProperty', backref='user')
    room = db.relationship('Room', backref='user', uselist=False)
    compere = db.relationship('Compere', backref='user', uselist=False)
    phone = db.relationship('PhoneBinding', backref='user', uselist=False)
    payment = db.relationship('Payment', backref='user')
    device = db.relationship('Device', backref='user', uselist=False)
    verification = db.relationship('CompereVerification', backref='user', uselist=False)
    withdrawal = db.relationship('WithdrawHistory', backref='user')


class UserCertification(db.Model):
    __tablename__ = "user_certs"

    nickname = db.Column(db.String(128), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    created_time = db.Column(db.DateTime(timezone=True))


class Device(db.Model):
    device_id = db.Column("did", db.Integer, primary_key=True)
    udid = db.Column(db.String(128))
    enabled = db.Column(db.Boolean)
    device_info = db.Column(JSON)


class UserProperty(db.Model):
    __tablename__ = "user_property"

    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    vcy = db.Column(db.Integer)
    vfc = db.Column(db.Integer)


class Room(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    name = db.Column(db.String(256))
    bulletin = db.Column(db.Text)
    on_air = db.Column("is_lived", db.Boolean)
    screenshot = db.Column(db.String(256))
    enable = db.Column(db.Boolean)
    disable_time = db.Column(db.DateTime(timezone=False))
    created_time = db.Column(db.DateTime(timezone=False))
    control_flag = db.Column(db.Integer)
    game_id = db.Column(db.Integer)
    chatroom = db.Column(db.Integer)


class Compere(db.Model):
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    rid = db.Column(db.Integer, db.ForeignKey('room.rid'))
    image = db.Column(db.String(128))
    description = db.Column("descs", db.Text)
    auth_status = db.Column(db.Boolean)
    tags = db.Column(db.String(128))
    stat = db.relationship('RoomStat', backref='compere', uselist=False)


class RoomStat(db.Model):
    __tablename__ = "room_statistical"

    rid = db.Column(db.Integer, db.ForeignKey('room.rid'), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('compere.uid'))
    num_audience = db.Column(db.Integer, default=0)
    num_follows = db.Column(db.Integer, default=0)
    num_popularity = db.Column(db.Integer, default=0)
    num_likes = db.Column(db.Integer, default=0)
    num_live = db.Column(db.Integer, default=0)
    num_subscription = db.Column(db.Integer, default=0)


class PhoneBinding(db.Model):
    __tablename__ = "phone_bindings"
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    phone = db.Column(db.String(64), primary_key=True)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user_certs.uid'))
    contact = db.Column(db.String(128))
    body = db.Column(db.Text)
    status = db.Column("state", db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=False))
    cert = db.relationship('UserCertification', backref='feedback', uselist=False)


class GiftGiving(db.Model):
    __tablename__ = "income_log"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    compere_id = db.Column(db.Integer, db.ForeignKey('users.uid'))
    prop_id = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    value = db.Column("t_price", db.Integer)
    currency = db.Column("money_type", db.String(12))
    send_time = db.Column(db.DateTime(timezone=False))
    user = db.relationship('AppUser', backref='presenter', foreign_keys=uid)
    compere = db.relationship('AppUser', backref='recipient', foreign_keys=compere_id)


class WithdrawHistory(db.Model):
    __tablename__ = "draw_history"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    apply_time = db.Column(db.Integer, nullable=False)
    deal_time = db.Column(db.Integer)
    status = db.Column(db.Integer, default=1)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    vfc_amount = db.Column(db.Float, nullable=False, default=0)
    vcy_amount = db.Column(db.Float, nullable=False, default=0)
    before_vfc_amount = db.Column(db.Float, nullable=False, default=0)
    after_vfc_amount = db.Column(db.Float, nullable=False, default=0)


class Payment(db.Model):
    __tablename__ = "payment_history"

    order_id = db.Column(db.String(128), primary_key=True)
    trans_id = db.Column(db.String(128))
    uuid = db.Column(UUID, db.ForeignKey('users.uuid'))
    complete_time = db.Column(db.DateTime(timezone=False))
    success = db.Column(db.Boolean)
    currency = db.Column(db.String(64))
    money = db.Column(db.Float)
    product_id = db.Column(db.String(128))
    pay_type = db.Column(db.String(64))


class CompereVerification(db.Model):
    __tablename__ = "compere_check"

    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    real_name = db.Column(db.String(128), nullable=False)
    card_id = db.Column(db.String(128), nullable=False)
    id_card_front = db.Column("positive", db.String(128), nullable=False)
    status = db.Column("check_status", db.Boolean)
    commit_time = db.Column(db.DateTime(timezone=False))
    id_card_back = db.Column("negative", db.String(128), nullable=False)
    phtot_in_hand = db.Column("hand", db.String(128), nullable=False)
    bankcard_no = db.Column(db.String(128), nullable=False)
    ccid = db.Column(db.Integer, primary_key=True)


class Banner(db.Model):
    __tablename__ = "roll"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.rid'))
    room_name = db.Column("room", db.String(64))
    image = db.Column(db.String(256))
    compere_id = db.Column("compere_id", db.Integer, db.ForeignKey('users.uid'))
    compere_uuid = db.Column("compereid", UUID)
    login_name = db.Column("compere", db.String(128))
    flag = db.Column(db.String(32))
    position = db.Column("pos", db.Integer)
    url = db.Column(db.String(256))
    room = db.relationship('Room', backref='banner', uselist=False)
    compere = db.relationship('AppUser', backref='banner', uselist=False)


class Broadcast(db.Model):
    id = db.Column(db.String(128), primary_key=True)
    index_num = db.Column(db.Integer)
    broadcast_content = db.Column(db.Text)
    created_time = db.Column(db.DateTime(timezone=False), nullable=False)
    start_time = db.Column(db.DateTime(timezone=False))
    end_time = db.Column(db.DateTime(timezone=False))
    broadcast_range = db.Column(db.String(32))
    status = db.Column(db.Integer, nullable=False)
    target = db.Column(db.String)
    broadcast_interval = db.Column(db.Integer, nullable=False, default=60)


class RoomTags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    mode = db.Column(db.Integer)
    weight = db.Column(db.Integer)


if __name__ == '__main__':
    pass