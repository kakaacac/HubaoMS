# -*- coding: utf-8 -*-
import json
import time
import requests
from datetime import datetime, timedelta
from math import ceil
from sqlalchemy.sql import func
from flask import flash, redirect, url_for, request
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from forms import TaskEditForm, DateSelectForm
from utils.html_element import colorize, button
from utils.formatter import format_thumbnail, format_account_action,format_room_action, format_room_status, \
    format_user_action, prop_name, prop_type, format_present_value, ts_to_time, format_account_status
from models import db, AppUser, UserProperty, Feedback, GiftGiving, WithdrawHistory, Payment, Room
from config import TASK_CONFIG, PAGE_SIZE, VIDEO_API_KEY, VIDEO_API_DOMAIN
from utils.functions import is_file_exists, hash_md5
from utils import redis, netease, job_queue


class UserView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

    column_auto_select_related = True
    column_list = ("uid", "cert.nickname", "display_name", "avatar", "sex", "compere.auth_status", "phone.phone",
                   "cert.created_time", "level", "actions")
    column_filters = ("level", "compere.auth_status")
    column_default_sort = "uid"
    column_searchable_list = ("uid", "cert.nickname", "phone.phone", "display_name")
    column_sortable_list = ("uid", "cert.nickname", "sex", "compere.auth_status", "cert.created_time", "level", "display_name")
    column_labels = {
        "uid": u"用户 ID",
        "cert.nickname": u"登录名",
        "display_name": u"用户昵称",
        "avatar": u"头像",
        "sex": u"性别",
        "compere.auth_status": u"认证主播",
        "phone.phone": u"电话",
        "cert.created_time": u"注册时间",
        "level": u"等级",
        "actions": u"其他信息"
    }
    column_formatters = {"avatar": format_thumbnail("avatar"),
                         "sex": lambda v, c, m, n: m.sex.get("sex", "") if m.sex else None,
                         "compere.auth_status": lambda v, c, m, n: u"是" if m.compere and m.compere.auth_status else u"否",
                         "cert.created_time": lambda v, c, m, n: m.cert.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                         "actions": format_user_action}

    list_template = "indexed_thumbnail_list.html"

    def is_accessible(self):
        return current_user.is_authenticated

    @expose("/gift_giving/<uid>")
    def gift_giving_detail(self, uid):
        def pager_url(p):
            return url_for(".gift_giving_detail", page=p+1, uid=uid)

        page = int(request.args.get("page", 1))
        records = GiftGiving.query.filter_by(uid=uid).paginate(page, PAGE_SIZE, False)

        kwargs = {
            "uid": uid,
            "data": records.items,
            "prop_name": prop_name,
            "format_value": format_present_value,
            "prop_type": prop_type,
            "num_pages": records.pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": PAGE_SIZE,
            "total": records.total
        }

        return self.render("user/gift_present_detail.html", **kwargs)


    @expose("/recharge_detail/<uid>")
    def recharge_detail(self, uid):
        def pager_url(p):
            return url_for(".recharge_detail", page=p+1, uid=uid)

        page = int(request.args.get("page", 1))
        payments = Payment.query.filter_by(user=AppUser.query.get(uid)).paginate(page, PAGE_SIZE, False)

        kwargs = {
            "uid": uid,
            "data": payments.items,
            "num_pages": payments.pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": PAGE_SIZE,
            "total": payments.total
        }
        return self.render("user/recharge_detail.html", **kwargs)


    @expose("/property_info/<uid>")
    def property_info(self, uid):
        def pager_url(p):
            return url_for(".property_info", page=p+1, uid=uid)

        user_property = UserProperty.query.get(uid)
        grass = user_property.vfc if user_property else 0
        bone = user_property.vcy if user_property else 0
        amber = db.session.query(func.sum(GiftGiving.value)).filter_by(compere_id=uid, currency="vcy").one()[0] or 0

        page = int(request.args.get("page", 1))
        records = WithdrawHistory.query.filter_by(uid=uid, status=4).paginate(page, PAGE_SIZE, False)

        items = records.items
        for item in items:
            setattr(item, "total_exchanged",
                    db.session.query(func.sum(WithdrawHistory.amount)).filter(WithdrawHistory.uid == uid,
                                                                              WithdrawHistory.status == 4,
                                                                              WithdrawHistory.apply_time <= item.apply_time).one()[0] or 0)
        kwargs = {
            "uid": uid,
            "data": items,
            "ts_to_time": ts_to_time,
            "grass": grass,
            "bone": bone,
            "amber": amber,
            "num_pages": records.pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": PAGE_SIZE,
            "total": records.total
        }

        return self.render("user/user_property.html", **kwargs)


    @expose("/other_info/<uid>")
    def other_info(self, uid):
        user = AppUser.query.get(uid)
        kwargs = {
            "uuid": user.uuid,
            "device_id": user.device.udid,
            "level": user.level,
            "exp": user.exp,
            "vip": u"是" if user.vip else u"否",
            "amber": db.session.query(func.sum(GiftGiving.value)).filter_by(compere_id=uid, currency="vcy").one()[0] or 0
        }
        return self.render("user/user_extra_info.html", **kwargs)


class FeedbackView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

    column_auto_select_related = True
    column_list = ("id", "uid", "cert.nickname", "cert.user.display_name", "contact", "body", "created_at", "status", "action")
    column_default_sort = "id"
    column_searchable_list = ("uid", "cert.nickname", "contact", "cert.user.display_name")
    column_sortable_list = ("uid", "cert.nickname", "created_at", "status", "cert.user.display_name")
    column_labels = {
        "uid": u"用户 ID",
        "cert.nickname": u"登录名",
        "contact": u"联系方式",
        "body": u"反馈内容",
        "created_at": u"创建时间",
        "status": u"是否已处理",
        "action": u"操作",
        "cert.user.display_name": u"用户昵称"
    }
    column_formatters = {"status": lambda v, c, m, n: u"是" if m.status else colorize(u"否", "red"),
                         "created_at": lambda v, c, m, n: m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                         "action": lambda v, c, m, n: button([(u"设为已处理", url_for("feedback.process", fid=m.id))]) if m.status == 0 else None}

    def is_accessible(self):
        return current_user.is_authenticated

    @expose("/process/<fid>")
    def process(self, fid):
        feedback = Feedback.query.get(fid)
        feedback.status = 1
        db.session.commit()
        flash(u"操作成功", category="info")
        return redirect(url_for("feedback.index_view"))


class TaskView(BaseView):
    def __init__(self, name=None, category=None, endpoint=None, url=None,
                 static_folder=None, static_url_path=None,
                 menu_class_name=None, menu_icon_type=None, menu_icon_value=None):
        super(TaskView, self).__init__(name, category, endpoint, url, static_folder, static_url_path,
                                       menu_class_name, menu_icon_type, menu_icon_value)

        with open(TASK_CONFIG) as f:
            self.tasks = json.load(f)

        self.vc_options = [("vfc", u"二级货币"), ("vcy", u"一级货币")]
        self.prop_options = [
            ("1", u"小草"),
            ("2", u"猴赛雷"),
            ("3", u"晚安"),
            ("4", u"豹豹"),
            ("5", u"小鲜肉"),
            ("6", u"时光鸡")
        ]

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/')
    def task_list(self):
        for i, task in enumerate(self.tasks):
            award_info = task["prize"].split(":")
            self.tasks[i].update({
                "award_type": award_info[0],
                "currency": award_info[1],
                "amount": award_info[2]
            })
        return self.render("user/task.html", data=self.tasks)

    @expose('/edit/<task_id>', methods=["GET",])
    def task_edit_view(self, task_id):
        tasks = reduce(lambda x, y: x.update({y.get("task_id"):y}) or x, self.tasks, {})
        task = tasks.get(task_id)
        award_info = task["prize"].split(":")

        form = TaskEditForm()
        form.task_name.data = task["task"]
        form.task_desc.data = task["task_desc"]
        form.award_type.data = award_info[0]
        form.award_amount.data = award_info[2]
        form.img_url.data = task["img"]
        form.display.data = task["display"]
        form.task_type.data = task["task_type"].lower()

        vc_str = json.dumps(self.vc_options, ensure_ascii=False)
        prop_str = json.dumps(self.prop_options, ensure_ascii=False)

        return self.render("user/task_edit.html",
                           form=form,
                           action=url_for('.edit_task', task_id=task_id),
                           vc_options=vc_str,
                           prop_options=prop_str,
                           cancel=url_for('.task_list'),
                           title=u'修改任务')

    @expose('/edit/<task_id>', methods=["POST",])
    def edit_task(self, task_id):
        form = TaskEditForm()
        if not form.validate_on_submit():
            flash(u"缺少关键信息", category="error")
            return redirect(url_for('.task_edit_view', task_id=task_id))

        if not is_file_exists(form.img_url.data):
            flash(u"请先上传图片", category="error")
            return redirect(url_for('.task_edit_view', task_id=task_id))

        with open(TASK_CONFIG) as f:
            task_info = json.load(f)
            for task in task_info:
                if task.get("task_id") == task_id:
                    task["task"] = form.task_name.data
                    task["img"] = form.img_url.data
                    task["task_type"] = form.task_type.data
                    task["task_desc"] = form.task_desc.data
                    task["display"] = form.display.data
                    task["prize"] = ":".join([form.award_type.data,
                                              request.form["award_currency"],
                                              "{:4f}".format(form.award_amount.data).rstrip('0').rstrip('.')])
                    break

        with open(TASK_CONFIG, 'w') as f:
            json.dump(task_info, f, indent=2)

        self.tasks = task_info

        flash(u"修改成功", category="info")
        return redirect(url_for(".task_list"))

    @expose('/create')
    def create_task_view(self):
        form = TaskEditForm()
        vc_str = json.dumps(self.vc_options, ensure_ascii=False)
        prop_str = json.dumps(self.prop_options, ensure_ascii=False)

        return self.render("user/task_edit.html",
                           form=form,
                           action=url_for('.create_task'),
                           vc_options=vc_str,
                           prop_options=prop_str,
                           cancel=url_for('.task_list'),
                           title=u'添加任务')

    @expose('/create', methods=('POST',))
    def create_task(self):
        form = TaskEditForm()
        if not form.validate_on_submit():
            flash(u"信息有误或缺失", category="error")
            return redirect(url_for('.create_task_view'))

        if not is_file_exists(form.img_url.data):
            flash(u"请先上传图片", category="error")
            return redirect(url_for('.create_task_view'))

        with open(TASK_CONFIG) as f:
            task_info = json.load(f)

            task_info.append(
                {
                    "task_type": form.task_type.data,
                    "task_id": str(len(task_info) + 1),
                    "img": form.img_url.data,
                    "task": form.task_name.data,
                    "task_desc": form.task_desc.data,
                    "display": form.display.data,
                    "prize": ":".join([form.award_type.data,
                                       request.form["award_currency"],
                                       "{:4f}".format(form.award_amount.data).rstrip('0').rstrip('.')])
                }
            )

        with open(TASK_CONFIG, 'w') as f:
            json.dump(task_info, f, indent=2)

        self.tasks = task_info

        flash(u"任务添加成功", category="info")
        return redirect(url_for(".task_list"))

    @expose('/delete/<task_id>')
    def delete_task(self, task_id):
        with open(TASK_CONFIG) as f:
            task_info = json.load(f)
            for i, task in enumerate(task_info):
                if task.get("task_id") == task_id:
                    task_info.pop(i)
                    break

        with open(TASK_CONFIG, 'w') as f:
            json.dump(task_info, f, indent=2)

        self.tasks = task_info

        flash(u"删除成功", category="info")
        return redirect(url_for(".task_list"))


def unblock_account_job(uid):
    # To avoid circular import, should be improved later
    from app import app
    with app.app_context():
        user = AppUser.query.get(uid)
        if user.locked:
            user.locked = False
            db.session.commit()
            redis.master().hdel("control:block:account", user.uuid.replace("-", ""))


def unblock_room_job(rid):
    # To avoid circular import, should be improved later
    from app import app
    with app.app_context():
        room = Room.query.get(rid)
        if not room.enable:
            #restore video stream
            AccountManagementView.control_video_stream(room.rid, room.user.uuid, action=1)
            room.enable = True
            room.control_flag = 0
            db.session.commit()
            redis.master().hdel("control:block:room", rid)


class AccountManagementView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

    column_auto_select_related = True
    column_list = ("uid", "cert.nickname", "display_name", "locked", "locked_time", "acc_action",
                   "room.control_flag", "room.disable_time", "room_action")
    column_default_sort = "uid"
    column_searchable_list = ("uid", "cert.nickname", "display_name")
    column_sortable_list = ("uid", "cert.nickname", "locked", "locked_time",
                            "room.control_flag", "room.disable_time", "display_name")
    column_labels = {
        "uid": u"用户 ID",
        "cert.nickname": u"登录名",
        "locked": u"用户账号状态",
        "locked_time": u"账号最近封停时间",
        "acc_action": u"账号操作",
        "room.control_flag": u"用户直播间状态",
        "room.disable_time": u"直播间最近封停时间",
        "room_action": u"直播间操作",
        "display_name": u"用户昵称"
    }
    column_formatters = {
        "locked": format_account_status,
        "locked_time": lambda v, c, m, n: m.locked_time.strftime("%Y-%m-%d %H:%M:%S") if m.locked_time else None,
        "room.control_flag": format_room_status,
        "room.disable_time": lambda v, c, m, n: m.room.disable_time.strftime("%Y-%m-%d %H:%M:%S") if m.room and m.room.disable_time else None,
        "acc_action": format_account_action,
        "room_action": format_room_action
    }
    list_template = "user/account_management.html"

    def is_accessible(self):
        return current_user.is_authenticated

    # Override index_view function
    @expose('/')
    def index_view(self):
        """
            List view
        """
        if self.can_delete:
            delete_form = self.delete_form()
        else:
            delete_form = None

        # Grab parameters from URL
        view_args = self._get_list_extra_args()

        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        # Get count and data
        count, data = self.get_list(view_args.page, sort_column, view_args.sort_desc,
                                    view_args.search, view_args.filters)

        list_forms = {}
        if self.column_editable_list:
            for row in data:
                list_forms[self.get_pk_value(row)] = self.list_form(obj=row)

        # Calculate number of pages
        if count is not None and self.page_size:
            num_pages = int(ceil(count / float(self.page_size)))
        elif not self.page_size:
            num_pages = 0  # hide pager for unlimited page_size
        else:
            num_pages = None  # use simple pager

        # Various URL generation helpers
        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None

            return self._get_list_url(view_args.clone(page=p))

        def sort_url(column, invert=False):
            desc = None

            if invert and not view_args.sort_desc:
                desc = 1

            return self._get_list_url(view_args.clone(sort=column, sort_desc=desc))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        clear_search_url = self._get_list_url(view_args.clone(page=0,
                                                              sort=view_args.sort,
                                                              sort_desc=view_args.sort_desc,
                                                              search=None,
                                                              filters=None))

        # Interaction form
        form = DateSelectForm()

        return self.render(
            account_form=form,
            room_form=form,

            template=self.list_template,
            data=data,
            list_forms=list_forms,
            delete_form=delete_form,

            # List
            list_columns=self._list_columns,
            sortable_columns=self._sortable_columns,
            editable_columns=self.column_editable_list,
            list_row_actions=self.get_list_row_actions(),

            # Pagination
            count=count,
            pager_url=pager_url,
            num_pages=num_pages,
            page=view_args.page,
            page_size=self.page_size,

            # Sorting
            sort_column=view_args.sort,
            sort_desc=view_args.sort_desc,
            sort_url=sort_url,

            # Search
            search_supported=self._search_supported,
            clear_search_url=clear_search_url,
            search=view_args.search,

            # Filters
            filters=self._filters,
            filter_groups=self._get_filter_groups(),
            active_filters=view_args.filters,

            # Actions
            actions=actions,
            actions_confirmation=actions_confirmation,

            # Misc
            enumerate=enumerate,
            get_pk_value=self.get_pk_value,
            get_value=self.get_list_value,
            return_url=self._get_list_url(view_args),
        )

    @expose("/block/<uid>")
    def block_account(self, uid):
        user = AppUser.query.get(uid)
        if user.locked:
            flash(u"用户已被封禁", category="info")
            return redirect(url_for("account.index_view"))
        else:
            user.locked = True
            user.locked_time = datetime.now()
            db.session.commit()
            flash(u"封停成功", category="warning")
            return redirect(url_for("account.index_view"))

    @expose("/unblock/<uid>")
    def unblock_account(self, uid):
        user = AppUser.query.get(uid)
        if user.locked:
            user.locked = False
            db.session.commit()
            redis.master().hdel("control:block:account", user.uuid.replace("-", ""))
            flash(u"解封成功", category="info")
            return redirect(url_for("account.index_view"))
        else:
            flash(u"用户未被封禁", category="info")
            return redirect(url_for("account.index_view"))

    @expose("/suspend_room/<rid>")
    def suspend_room(self, rid):
        room = Room.query.get(rid)
        if room.enable:
            room_id = room.rid
            end_time = int(time.time()) + 300

            zadd = redis.master().zadd("expires:room.ctrl.1", end_time, room_id)

            rec_key = "control:rectification." + datetime.today().strftime("%Y-%m-%d")
            rec_num = redis.master().hincrby(rec_key, room_id, 1)
            if rec_num == 1:
                redis.master().expireat(rec_key, int(time.mktime((datetime.now() + timedelta(days=1)).timetuple())))

            if rec_num >= 10:
                return self.block_room(rid)

            # send NetEase message
            net = self.send_block_room_msg(room.chatroom, 1)

            room.control_flag = 1
            db.session.commit()

            if zadd and rec_num and net:
                flash(u"勒令整改成功", category="warning")
            else:
                flash(u"操作失败", category="error")
            return redirect(url_for("account.index_view"))
        else:
            flash(u"房间已被封停", category="info")
            return redirect(url_for("account.index_view"))

    @expose("/block_room/<rid>")
    def block_room(self, rid):
        room = Room.query.get(rid)
        if room.enable:
            # send NetEase message
            self.send_block_room_msg(room.chatroom, 2)

            #cut off video stream
            self.control_video_stream(rid, room.user.uuid)

            if room.control_flag == 1:
                redis.master().zrem("expires:room.ctrl.1", rid)

            room.enable = False
            room.control_flag = 2
            room.disable_time = datetime.now()
            db.session.commit()
            flash(u"封停成功", category="warning")
            return redirect(url_for("account.index_view"))
        else:
            flash(u"房间已被封停", category="info")
            return redirect(url_for("account.index_view"))

    @expose("/unblock_room/<rid>")
    def unblock_room(self, rid):
        room = Room.query.get(rid)
        if room.enable:
            flash(u"房间未被封停", category="info")
            return redirect(url_for("account.index_view"))
        else:
            #restore video stream
            self.control_video_stream(room.rid, room.user.uuid, action=1)

            room.enable = True
            room.control_flag = 0
            db.session.commit()
            redis.master().hdel("control:block:room", rid)
            flash(u"解封成功", category="info")
            return redirect(url_for("account.index_view"))

    @expose("/temporary_block/<uid>", methods=['POST',])
    def temporary_block_account(self, uid):
        user = AppUser.query.get(uid)
        if user.locked:
            flash(u"用户已被封禁", category="info")
            return redirect(url_for("account.index_view"))
        else:
            form = DateSelectForm()
            if form.validate_on_submit():
                block_time = int(form.custom.data) if form.date.data == "custom" else int(form.date.data)
                expired_time = datetime.now() + timedelta(seconds=block_time)

                # Store expiration info at redis
                redis.master().hset("control:block:account",
                                    user.uuid.replace("-", ""),
                                    expired_time.strftime("%Y-%m-%d %H:%M:%S"))

                # Add scheduler job for unblock
                job_queue.put({
                    "action": "add",
                    "func": unblock_account_job,
                    "trigger": 'date',
                    "job_kwargs": {
                        "args": (uid,),
                        "coalesce": True,
                        "misfire_grace_time": 86400,
                        "id": "block_account_{}".format(uid),
                        "run_date": expired_time
                    }
                })

                user.locked = True
                user.locked_time = datetime.now()
                db.session.commit()

                flash(u"封停成功", category="warning")
                return redirect(url_for("account.index_view"))
            else:
                flash(u"数据输入有误，操作失败", category="error")
                return redirect(url_for("account.index_view"))

    @expose("/temporary_block_room/<rid>", methods=['POST',])
    def temporary_block_room(self, rid):
        room = Room.query.get(rid)
        if room.enable:
            form = DateSelectForm()
            if form.validate_on_submit():
                block_time = int(form.custom.data) if form.date.data == "custom" else int(form.date.data)
                expired_time = datetime.now() + timedelta(seconds=block_time)

                #cut off video stream
                self.control_video_stream(rid, room.user.uuid)

                if room.control_flag == 1:
                    redis.master().zrem("expires:room.ctrl.1", rid)

                room.enable = False
                room.control_flag = 2
                room.disable_time = datetime.now()
                db.session.commit()

                # send NetEase message
                self.send_block_room_msg(room.chatroom, 2)

                # Store expiration info at redis
                redis.master().hset("control:block:room", rid, expired_time.strftime("%Y-%m-%d %H:%M:%S"))

                # Add scheduler job for unblock
                job_queue.put({
                    "action": "add",
                    "func": unblock_room_job,
                    "trigger": 'date',
                    "job_kwargs": {
                        "args": (rid,),
                        "coalesce": True,
                        "misfire_grace_time": 86400,
                        "id": "block_room_{}".format(rid),
                        "run_date": expired_time
                    }
                })

                flash(u"封停成功", category="warning")
                return redirect(url_for("account.index_view"))
            else:
                flash(u"数据输入有误，操作失败", category="error")
                return redirect(url_for("account.index_view"))
        else:
            flash(u"房间已被封停", category="info")
            return redirect(url_for("account.index_view"))

    @staticmethod
    def send_block_room_msg(chatroom_id, status):
        ext = {
            "action": "3003",
            "data": {"control_flag": str(status)}
        }
        response = netease.send_to_chatroom(chatroom_id, 100, ext=ext)
        return json.loads(response.content)["code"] == 200

    @staticmethod
    def control_video_stream(room_id, uuid, action=0, description=''):
        user_id = uuid.replace("-", "")
        password = str(int(time.time()))
        sign = hash_md5(user_id + password + str(action) + VIDEO_API_KEY)

        payload = {
            "userid": user_id,
            "roomid": room_id,
            "password": password,
            "operation": action,
            "closeldescribe": description,
            "sign": sign
        }
        return requests.get(VIDEO_API_DOMAIN, params=payload)

