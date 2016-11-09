# -*- coding: utf-8 -*-
from flask import flash, redirect, url_for
from flask_admin import BaseView, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        flash(u"请先登录", category='error')
        return redirect(url_for("login.index"))


class AuthenticatedModelView(ModelView, AuthenticatedBaseView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False


class IndexView(AdminIndexView):
    @expose()
    def index(self):
        authenticated = current_user.is_authenticated
        username = current_user.username if authenticated else None
        return self.render("index.html", authenticated=authenticated, current_user=username)