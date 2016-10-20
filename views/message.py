# -*- coding: utf-8 -*-
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_admin import expose
from flask import url_for, request

from utils.formatter import format_broadcast_actions, format_broadcast_range, format_broadcast_status
from models import Broadcast, RoomTags, Room
from forms import BroadcastEditForm
from utils.functions import json_response

class BroadcastView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

    column_auto_select_related = True
    column_filters = ("broadcast_range", "status")
    column_list = ("index_num", "broadcast_content", "created_time", "start_time", "end_time",
                   "broadcast_range", "status", "actions")
    column_default_sort = ("status", True)
    column_searchable_list = ("index_num",)
    column_sortable_list = ("index_num", "created_time", "start_time", "end_time", "broadcast_range", "status")
    column_labels = {
        "index_num": u"序号",
        "broadcast_content": u"广播内容",
        "created_time": u"创建时间",
        "start_time": u"开始时间",
        "end_time": u"结束时间",
        "broadcast_range": u"广播范围",
        "status": u"状态",
        "actions": u"操作"
    }
    column_formatters = {
        "created_time" : lambda v, c, m, n: m.created_time.strftime("%Y-%m-%d %H:%M:%S"),
        "start_time" : lambda v, c, m, n: m.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time" : lambda v, c, m, n: m.end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "broadcast_range": format_broadcast_range,
        "status": format_broadcast_status,
        "actions": format_broadcast_actions
    }
    list_template = "message/broadcast_view.html"

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/create')
    def create_broadcast_view(self):
        form = BroadcastEditForm()

        return self.render("message/broadcast_edit_view.html",
                           title=u"添加广播",
                           action=url_for(".create_broadcast"),
                           cancel=url_for(".index_view"),
                           form=form)

    @expose('create', methods=['POST',])
    def create_broadcast(self):
        pass

    @expose('/edit')
    def edit_broadcast_view(self, id):
        pass

    @expose('/stop')
    def stop_broadcast(self, id):
        pass

    @expose('/tags')
    def get_tags(self):
        tags = RoomTags.query.all()
        return json_response({
            "tags": [{"id": item.id, "name": item.name} for item in tags]
        }, 200)

    @expose('/rooms')
    def get_rooms(self):
        rooms = Room.query.filter_by(on_air=True, enable=True).all()
        room_list = [{"room_id": item.rid,
                      "room_name": item.name,
                      "login_name": item.user.cert.nickname,
                      "display_name": item.user.display_name} for item in rooms]

        return json_response({"rooms": room_list}, 200)