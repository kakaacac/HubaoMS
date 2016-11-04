# -*- coding: utf-8 -*-
from flask_admin import BaseView, expose
from flask import redirect, url_for, flash
from flask_login import login_user

from models import db, User
from forms import LoginForm

class AuthView(BaseView):

    @expose('/')
    def index(self):
        form = LoginForm()
        return self.render("auth/login.html", form=form)

    @expose('/login', methods=["GET"])
    def login(self):
        form = LoginForm()
        return self.render("auth/login.html", form=form)

    @expose('/login', methods=["POST"])
    def login(self):
        form = LoginForm()
        if form.validate_on_submit():
            user, authenticated = User.query.authenticate(form.username.data, form.password.data)
            if user and authenticated:
                login_user(user)
                return redirect(url_for("user.index_view"))
            else:
                print "not ok"
        flash("wrong!", category="error")
        return self.render("auth/login.html", form=form)

    @expose('/reg', methods=["POST"])
    def register(self):
        u = User("jaydentest", "123456", "test@hubao.tv")
        db.session.add(u)
        db.session.commit()