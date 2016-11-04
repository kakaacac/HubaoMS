# -*- coding: utf-8 -*-
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_admin import expose
from flask import url_for, request, flash, redirect
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime
import random
from string import ascii_lowercase, digits

from utils.formatter import format_broadcast_actions, format_broadcast_range, format_broadcast_status
from models import Broadcast, RoomTags, Room, db
from forms import BroadcastEditForm
from utils.functions import json_response, hash_md5
from utils import netease, job_queue


def send_broadcast(message, broadcast_range, tags=None, rooms=None):
    # To avoid circular import, should be improved later
    from app import app
    with app.app_context():
        if broadcast_range == 'tag':
            rooms = Room.query.filter(Room.on_air, Room.enable, Room.tags.overlap(tags)).all()
        elif broadcast_range == 'spec':
            rooms = Room.query.filter(Room.on_air, Room.enable, Room.rid.in_(rooms)).all()
        else:
            rooms = Room.query.filter_by(on_air=True, enable=True).all()

        netease.send_to_chatrooms([item.chatroom for item in rooms], 0, msg=message)


class BroadcastView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

    column_auto_select_related = True
    column_filters = ("broadcast_range",)
    column_list = ("broadcast_content", "created_time", "start_time", "end_time",
                   "broadcast_range", "status", "actions")
    column_default_sort = ("created_time", True)
    column_sortable_list = ("created_time", "start_time", "end_time", "broadcast_range")
    column_labels = {
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
        form = BroadcastEditForm()
        if form.validate_on_submit():
            broadcast = Broadcast()
            brdcst_id = self.generate_broadcast_id(form.content.data)
            value = [int(v) for v in form.target.data.split(',')] if form.target.data else None
            kwargs = {
                "message": form.content.data.encode('utf-8'),
                "broadcast_range": form.range.data,
                "tags": value,
                "rooms": value
            }

            broadcast.id = brdcst_id
            broadcast.broadcast_content = form.content.data
            broadcast.created_time = datetime.now()
            broadcast.start_time = form.start_time.data
            broadcast.end_time = form.end_time.data
            broadcast.broadcast_range = form.range.data
            broadcast.target = form.target.data
            broadcast.broadcast_interval = form.interval.data

            db.session.add(broadcast)
            db.session.commit()

            # Add scheduler job
            job_queue.put({
                "action": "add",
                "func": send_broadcast,
                "trigger": "interval",
                "job_kwargs": {
                    "kwargs": kwargs,
                    "minutes": form.interval.data,
                    "start_date": form.start_time.data,
                    "end_date": form.end_time.data,
                    "id": brdcst_id
                }
            })

            flash(u"添加广播成功", category="info")
            return redirect(url_for(".index_view"))
        else:
            flash(u"输入有误，添加失败", category="error")
            return redirect(url_for(".index_view"))


    @expose('/edit/<id>')
    def edit_broadcast_view(self, id):
        form = BroadcastEditForm()
        broadcast = Broadcast.query.get(id)

        form.content.data = broadcast.broadcast_content
        form.start_time.data = broadcast.start_time
        form.end_time.data = broadcast.end_time
        form.range.data = broadcast.broadcast_range
        form.target.data = broadcast.target
        form.interval.data = broadcast.broadcast_interval

        if broadcast.broadcast_range == 'tag':
            tag_list = broadcast.target.split(",")
            tags = RoomTags.query.filter(RoomTags.id.in_(tag_list)).all()
            display_value = ",".join([item.name for item in tags])
        else:
            display_value = broadcast.target

        return self.render("message/broadcast_edit_view.html",
                           title=u"修改广播",
                           action=url_for(".edit_broadcast", id=id),
                           cancel=url_for(".index_view"),
                           display_value=display_value,
                           form=form)

    @expose('/edit/<id>', methods=['POST',])
    def edit_broadcast(self, id):
        form = BroadcastEditForm()
        if form.validate_on_submit():
            broadcast = Broadcast.query.get(id)

            value = [int(v) for v in form.target.data.split(',')] if form.target.data else None
            kwargs = {
                "message": form.content.data.encode('utf-8'),
                "broadcast_range": form.range.data,
                "tags": value,
                "rooms": value
            }

            if not broadcast.interrupted:
                # Remove original job
                job_queue.put({
                    "action": "stop",
                    "id": id
                })
            else:
                broadcast.interrupted = False

            # Add new job
            job_queue.put({
                "action": "add",
                "func": send_broadcast,
                "trigger": "interval",
                "job_kwargs": {
                    "kwargs": kwargs,
                    "minutes": form.interval.data,
                    "start_date": form.start_time.data,
                    "end_date": form.end_time.data,
                    "id": id
                }
            })

            broadcast.broadcast_content = form.content.data
            broadcast.start_time = form.start_time.data
            broadcast.end_time = form.end_time.data
            broadcast.broadcast_range = form.range.data
            broadcast.target = form.target.data
            broadcast.broadcast_interval = form.interval.data

            db.session.commit()

            flash(u"修改广播成功", category="info")
            return redirect(url_for(".index_view"))
        else:
            flash(u"输入有误，修改失败", category="error")
            return redirect(url_for(".index_view"))

    @expose('/stop/<id>')
    def stop_broadcast(self, id):
        broadcast = Broadcast.query.get(id)
        if broadcast.end_time < datetime.now() or broadcast.interrupted:
            flash(u"广播已停止", category="error")
            return redirect(url_for(".index_view"))
        else:
            # Stop job
            job_queue.put({
                "action": "stop",
                "id": id
            })
            broadcast.interrupted = True
            db.session.commit()
            flash(u"停止广播成功", category="info")
            return redirect(url_for(".index_view"))

    @expose('/restart/<id>')
    def restart_broadcast(self, id):
        broadcast = Broadcast.query.get(id)
        if broadcast.end_time < datetime.now():
            flash(u"广播已过期", category="error")
            return redirect(url_for(".index_view"))
        elif not broadcast.interrupted:
            flash(u"广播启动中", category="error")
            return redirect(url_for(".index_view"))
        else:
            value = [int(v) for v in broadcast.target.split(',')] if broadcast.target else None
            kwargs = {
                "message": broadcast.broadcast_content.encode('utf-8'),
                "broadcast_range": broadcast.broadcast_range,
                "tags": value,
                "rooms": value
            }

            # Add new job
            job_queue.put({
                "action": "add",
                "func": send_broadcast,
                "trigger": "interval",
                "job_kwargs": {
                    "kwargs": kwargs,
                    "minutes": broadcast.broadcast_interval,
                    "start_date": broadcast.start_time,
                    "end_date": broadcast.end_time,
                    "id": id
                }
            })

            broadcast.interrupted = False
            db.session.commit()

            flash(u"重新启动广播成功", category="info")
            return redirect(url_for(".index_view"))

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

    @staticmethod
    def generate_broadcast_id(msg):
        t = str(int(time.time()))
        r = "".join([random.choice(digits + ascii_lowercase) for _ in range(4)])
        return hash_md5(t + r + str(msg.encode("utf-8")))