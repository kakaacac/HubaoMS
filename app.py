# -*- coding: utf-8 -*-
import logging
from flask import Flask
from flask_admin import Admin

from views import AuthView, UserView
from config import *

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{un}:{pw}@{h}:{p}/{db}".format(
    un=USER, pw=PASSWORD, h=HOST, p=PORT, db=DATABASE
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "test"

from models import db, login_manager, AppUser, UserCertification
db.init_app(app)
login_manager.init_app(app)

admin = Admin(app, name="Hubao TV", template_mode='bootstrap2')
admin.add_view(AuthView(name="Login", url='/account'))
admin.add_view(UserView(name="User", url='/user', session=db.session, model=AppUser))

if __name__ == '__main__':
    app.run(debug=True)