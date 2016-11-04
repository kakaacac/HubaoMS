# -*- coding: utf-8 -*-
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from utils.formatter import format_thumbnail, format_room_channel, format_boolean

class RoomView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

    column_auto_select_related = True
    column_list = ("rid", "uid", "user.cert.nickname", "channel", "name", "bulletin", "enable", "on_air",
                   "created_time", "screenshot", "chatroom")
    column_default_sort = "rid"
    column_searchable_list = ("rid", "uid", "user.cert.nickname", "name")
    column_sortable_list = ("uid", "rid", "user.cert.nickname", "enable", "on_air", "created_time")
    column_editable_list = ("bulletin", "name")
    column_labels = {
        "uid": u"主播 ID",
        "rid": u"房间 ID",
        "user.cert.nickname": u"登录名",
        "channel": u"频道分类",
        "name": u"房间名",
        "bulletin": u"房间公告",
        "enable": u"能否直播",
        "on_air": u"直播中",
        "created_time": u"创建时间",
        "screenshot": u"截图",
        "chatroom": u"聊天室 ID"
    }
    column_formatters = {
        "screenshot": format_thumbnail("screenshot"),
        "channel": format_room_channel,
        "enable": format_boolean("enable"),
        "on_air": format_boolean("on_air", true_color="green"),
        "created_time": lambda v, c, m, n: m.created_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    list_template = "thumbnail_list.html"

    def is_accessible(self):
        return current_user.is_authenticated