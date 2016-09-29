# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField, SubmitField,\
    TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired
from flask_admin.form import ImageUploadField

class LoginForm(Form):
    hidden = HiddenField()
    username = StringField(label="Username")
    password = PasswordField()
    submit = SubmitField(label="Login")


class TaskEditForm(Form):
    hidden = HiddenField()
    task_name = StringField(label=u"任务名称", validators=[DataRequired(),])
    task_desc = TextAreaField(label=u"任务描述")
    award_type = SelectField(label=u"任务奖励", choices=[("vc", u"虚拟货币"), ("prop", u"道具")])
    award_amount = FloatField(validators=[DataRequired(),])
    img_url = ""
    img = ImageUploadField()
    help_msg = ""
    display = SelectField(label=u"显示 or 隐藏", choices=[("display", u"显示"), ("hide", u"隐藏")])
    task_type = SelectField(label=u"任务类型", choices=[("onlyone", u"只能领取一次"), ("everyday", u"每天可领一次")])
    save = SubmitField(label=u"保存")
    cancel = SubmitField(label=u"取消")






