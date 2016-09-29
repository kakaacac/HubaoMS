# -*- coding: utf-8 -*-
import logging
from flask import Flask
from flask_admin import Admin

from views.user import UserView, FeedbackView, TaskView, AccountManagementView
from views.auth import AuthView
from views.compere import CompereView
from config import *
from models import db, AppUser, Feedback, Compere
from utils.login_manager import login_manager

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{un}:{pw}@{h}:{p}/{db}".format(
    un=USER, pw=PASSWORD, h=HOST, p=PORT, db=DATABASE
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "test"


db.init_app(app)
login_manager.init_app(app)

admin = Admin(app, name="Hubao TV", template_mode="bootstrap3")

# Auth
admin.add_view(AuthView(name="Login", url='/auth'))

# User
admin.add_view(UserView(name="User", category='User', endpoint='user', session=db.session, model=AppUser))
admin.add_view(FeedbackView(name="Feedback", endpoint='feedback', category='User', session=db.session, model=Feedback))
admin.add_view(TaskView(name="Task", category='User', endpoint='task'))
admin.add_view(AccountManagementView(name="Account", category="User", endpoint="account", session=db.session, model=AppUser))

# Compere
admin.add_view(CompereView(name="Compere", category="Compere", endpoint="compere", session=db.session, model=Compere))

if __name__ == '__main__':
    app.run(debug=True)
    # import json
    # print json.dump(json.load(open("task_backup.json")), open("task.txt", 'w'), indent=2)
