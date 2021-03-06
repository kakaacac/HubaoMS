# -*- coding: utf-8 -*-
from flask_admin import expose
from flask import url_for, flash, request
import time
from datetime import datetime
import random
from string import ascii_lowercase, digits

from base import AuthenticatedModelView
from utils.formatter import format_broadcast_actions, format_broadcast_range, format_broadcast_status
from models import Broadcast, RoomTags, Room, db, ScheduledJobs
from forms import BroadcastEditForm
from utils.functions import json_response, hash_md5, abs_redirect


class BroadcastView(AuthenticatedModelView):
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

    @staticmethod
    def get_chatrooms(broadcast_range, value):
        if broadcast_range == 'tag':
            rooms = Room.query.filter(Room.on_air, Room.enable, Room.tags.overlap(value)).all()
        elif broadcast_range == 'spec':
            rooms = Room.query.filter(Room.on_air, Room.enable, Room.rid.in_(value)).all()
        else:
            rooms = Room.query.filter_by(on_air=True, enable=True).all()
        return [item.chatroom for item in rooms]

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
            # TODO: get rooms on each execution
            rooms = self.get_chatrooms(form.range.data, value)

            kwargs = {
                "message": form.content.data.encode('utf-8'),
                "rooms": rooms
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

            # Add scheduler job
            job = ScheduledJobs()
            job.job_id = brdcst_id
            job.job_type = "interval"
            job.status = 0
            job.start_time = form.start_time.data
            job.end_time = form.end_time.data
            job.job_function = "broadcast"
            job.job_args = kwargs
            job.job_interval = form.interval.data

            db.session.add(job)

            db.session.commit()

            flash(u"添加广播成功", category="success")
            return abs_redirect(".index_view")
        else:
            flash(u"输入有误，添加失败", category="error")
            return abs_redirect(".index_view")


    @expose('/edit/<id>')
    def edit_broadcast_view(self, id):
        form = BroadcastEditForm()
        broadcast = Broadcast.query.get_or_404(id)

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
            broadcast = Broadcast.query.get_or_404(id)
            job = ScheduledJobs.query.get(id)

            value = [int(v) for v in form.target.data.split(',')] if form.target.data else None
            kwargs = {
                "message": form.content.data.encode('utf-8'),
                "rooms": self.get_chatrooms(form.range.data, value)
            }

            broadcast.broadcast_content = form.content.data
            broadcast.start_time = form.start_time.data
            broadcast.end_time = form.end_time.data
            broadcast.broadcast_range = form.range.data
            broadcast.target = form.target.data
            broadcast.broadcast_interval = form.interval.data

            # Modify scheduler job
            if job.status == 2:
                job.status = 0
            job.start_time = form.start_time.data
            job.end_time = form.end_time.data
            job.job_args = kwargs
            job.job_interval = form.interval.data

            db.session.commit()

            flash(u"修改广播成功", category="success")
            return abs_redirect(".index_view")
        else:
            flash(u"输入有误，修改失败", category="error")
            return abs_redirect(".index_view")

    @expose('/stop/<id>')
    def stop_broadcast(self, id):
        broadcast = Broadcast.query.get_or_404(id)
        if broadcast.end_time < datetime.now() or broadcast.interrupted:
            flash(u"广播已停止", category="error")
            return abs_redirect(".index_view")
        else:
            # Stop job
            job = ScheduledJobs.query.get(id)
            job.status = 1
            broadcast.interrupted = True
            db.session.commit()
            flash(u"停止广播成功", category="success")
            return abs_redirect(".index_view", **request.args)

    @expose('/restart/<id>')
    def restart_broadcast(self, id):
        broadcast = Broadcast.query.get_or_404(id)
        if broadcast.end_time < datetime.now():
            flash(u"广播已过期", category="error")
            return abs_redirect(".index_view")
        elif not broadcast.interrupted:
            flash(u"广播启动中", category="error")
            return abs_redirect(".index_view")
        else:
            job = ScheduledJobs.query.get(id)
            job.status = 0

            broadcast.interrupted = False
            db.session.commit()

            flash(u"重新启动广播成功", category="success")
            return abs_redirect(".index_view", **request.args)

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