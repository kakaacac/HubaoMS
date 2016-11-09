# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField, SubmitField,\
    TextAreaField, SelectField, FloatField, IntegerField, BooleanField
from wtforms.fields.html5 import DateTimeField
from wtforms.validators import DataRequired, Optional, NumberRange, ValidationError
from flask_admin.form import ImageUploadField
from flask_admin.form.widgets import DateTimePickerWidget

class LoginForm(Form):
    hidden = HiddenField()
    username = StringField(label="Username")
    password = PasswordField()
    remember = BooleanField(label="Remember me")
    submit = SubmitField(label="Login")


class TaskEditForm(Form):
    hidden = HiddenField()
    task_name = StringField(label=u"任务名称", validators=[DataRequired(),])
    task_desc = TextAreaField(label=u"任务描述")
    award_type = SelectField(label=u"任务奖励", choices=[("vc", u"虚拟货币"), ("prop", u"道具")])
    award_amount = FloatField(validators=[DataRequired(),])
    img_url = StringField(label=u"图片地址", render_kw={"readonly":True})
    img = ImageUploadField()
    help_msg = u"仅支持 gif, jpg, jpeg, png, tiff 格式"
    display = SelectField(label=u"显示 or 隐藏", choices=[("display", u"显示"), ("hide", u"隐藏")])
    task_type = SelectField(label=u"任务类型", choices=[("onlyone", u"只能领取一次"), ("everyday", u"每天可领一次")])
    save = SubmitField(label=u"保存")
    cancel = SubmitField(label=u"取消")


class CompereConfigurationForm(Form):
    hidden = HiddenField()
    conf = SelectField(label=u"是否需要认证", choices=[("1", u"是"), ("0", u"否")])
    save = SubmitField(label=u"保存")


class BannerEditForm(Form):
    hidden = HiddenField()
    query_type = SelectField(label=u"查询方式", choices=[("room_id", u"房间ID"), ("login_name", u"登录名")])
    query_info = StringField()
    img_url = StringField(label=u"图片地址", render_kw={"readonly":True}, validators=[DataRequired(),])
    img = ImageUploadField()
    help_msg = u"仅支持 gif, jpg, jpeg, png, tiff 格式"
    position = SelectField(label=u"位置", choices=[("0", u"首页"), ("1", u"互动"), ("2", u"热播")], validators=[DataRequired(),])
    room_id = StringField(label=u"房间 ID", render_kw={"readonly":True}, validators=[DataRequired(),])
    room_name = StringField(label=u"房间名称", render_kw={"readonly":True}, validators=[DataRequired(),])
    login_name = StringField(label=u"主播登录名", render_kw={"readonly":True}, validators=[DataRequired(),])
    compere_id = StringField(label=u"主播 ID", render_kw={"readonly":True}, validators=[DataRequired(),])
    banner_type = SelectField(label=u"轮播图类型", choices=[("room", u"普通"), ("web", u"网页")])
    redirect_url = StringField(label=u"跳转地址")
    save = SubmitField(label=u"保存")
    cancel = SubmitField(label=u"取消")


class DateSelectForm(Form):
    hidden = HiddenField()
    date = SelectField(label=u"日期", choices=[("1", u"1天"), ("3", u"3天"), ("7", u"7天"),
                                             ("30", u"30天"), ("custom", u"自定义")])
    custom = IntegerField(label=u"自定义日期", validators=[Optional(), NumberRange(min=1)])


def validate_end_time(form, field):
    if field.data < form.start_time.data or field.data + timedelta(seconds=30) < datetime.now():
        raise ValidationError("Invalid end time")


def validate_target(form, field):
    if form.range.data != 'all' and not field.data:
        raise ValidationError("Target cannot be empty")


class BroadcastEditForm(Form):
    hidden = HiddenField()
    content = TextAreaField(label=u"广播内容")
    start_time = DateTimeField(label=u"生效时间", default=datetime.now, validators=[DataRequired(),], widget=DateTimePickerWidget())
    end_time = DateTimeField(label=u"结束时间", default=datetime.now, validators=[DataRequired(), validate_end_time], widget=DateTimePickerWidget())
    interval = IntegerField(label=u"广播间隔", validators=[DataRequired(), NumberRange(min=1)], default=60)
    range = SelectField(label=u"范围", choices=[("all", u"全部"), ("tag", u"分类"), ("spec", u"指定")], default="all")
    target = TextAreaField(label=u"目标", validators=[validate_target,])
    save = SubmitField(label=u"保存")
    cancel = SubmitField(label=u"取消")






