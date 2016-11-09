# -*- coding: utf-8 -*-
from flask_admin import BaseView, expose
from flask import redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user

from models import db, User
from forms import LoginForm
from views.base import AuthenticatedBaseView

class LoginView(BaseView):
    def is_accessible(self):
        return not current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.index"))

    @expose()
    def index(self):
        form = LoginForm()
        return self.render("auth/login.html", form=form)

    @expose(methods=["POST"])
    def login(self):
        form = LoginForm()
        if form.validate_on_submit():
            user, authenticated = User.query.authenticate(form.username.data, form.password.data)
            if user and authenticated:
                login_user(user, remember=form.remember.data)
                return redirect(url_for("user.index_view"))
            else:
                flash("Invalid auth info", category="error")
                return redirect(url_for(".index"))
        flash("Invalid Input!", category="error")
        return redirect(url_for(".index"))

    @expose('/reg', methods=["POST"])
    def register(self):
        key = request.form.get("key")
        if key == "jayden":
            username = request.form.get("username")
            password = request.form.get("password")
            email = request.form.get("email")
            if username and password and email:
                u = User(username, password, email)
                db.session.add(u)
                db.session.commit()
                return "ok"
        return "fail"


class LogoutView(AuthenticatedBaseView):
    @expose()
    def logout_view(self):
        logout_user()
        return self.render("auth/logout.html")
