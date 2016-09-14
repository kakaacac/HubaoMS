# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import HiddenField, BooleanField, StringField, PasswordField, SubmitField

class LoginForm(Form):

    hidden = HiddenField()

    username = StringField(label="Username")

    password = PasswordField()

    submit = SubmitField(label="Login")
