# -*- coding: utf-8 -*-
from flask import flash, redirect
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from forms.account import LoginForm
from flask_login import login_user, logout_user, login_required, current_user

from models import User, db, AppUser, UserCertification, UserProperty

class AuthView(BaseView):

    @expose('/')
    def index(self):
        form = LoginForm()
        return self.render("login.html", form=form)

    @expose('/login', methods=["GET"])
    def login(self):
        form = LoginForm()
        return self.render("login.html", form=form)

    @expose('/login', methods=["POST"])
    def login(self):
        form = LoginForm()
        if form.validate_on_submit():
            user, authenticated = User.query.authenticate(form.username.data, form.password.data)
            if user and authenticated:
                login_user(user)
                return redirect("/user")
            else:
                print "not ok"
        flash("wrong!", category="error")
        return self.render("login.html", form=form)

    @expose('/reg', methods=["POST"])
    def register(self):
        u = User("jaydentest", "123456", "test@hubao.tv")
        db.session.add(u)
        db.session.commit()


class UserView(ModelView):
    # inline_models = [(UserProperty, dict(form_columns=["vcy"]))]

    column_auto_select_related = True
    column_list = (AppUser.level, "room.rid", "cert.nickname")
    column_formatters = {"level": lambda v, c, m, p: "4 test" if m.level == 4 else m.level}

    def is_accessible(self):
        return current_user.is_authenticated
