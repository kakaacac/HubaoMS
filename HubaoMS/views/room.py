# -*- coding: utf-8 -*-
from sqlalchemy.sql import not_

from models import AppUser, Device
from base import BaseRobotToggleView
from utils.formatter import format_thumbnail, format_room_channel, format_boolean, format_username
from config import ROBOT_APP_ID


class RoomView(BaseRobotToggleView):
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
        "bulletin": u"主播签名",
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
        "created_time": lambda v, c, m, n: m.created_time.strftime("%Y-%m-%d %H:%M:%S"),
        "user.cert.nickname": format_username("user.cert.nickname")
    }

    list_template = "robot_toggle_view.html"

    def get_count_query(self, robot=True):
        if robot:
            return super(RoomView, self).get_count_query()
        else:
            return super(RoomView, self).get_count_query().join(AppUser).join(Device).\
                filter(not_(Device.device_info["app_id"].astext.in_(ROBOT_APP_ID)))

    def get_query(self, robot=True):
        if robot:
            return super(RoomView, self).get_query()
        else:
            return super(RoomView, self).get_query().join(AppUser).join(Device).\
                filter(not_(Device.device_info["app_id"].astext.in_(ROBOT_APP_ID)))