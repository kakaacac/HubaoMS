# -*- coding: utf-8 -*-
from flask_login import LoginManager

from models import User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.token_loader
def load_token(token):
    return User.query.filter_by(auth_key=token).first()