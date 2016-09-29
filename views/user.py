# -*- coding: utf-8 -*-
import json
import hashlib
import os
from PIL import Image
from datetime import datetime
from sqlalchemy.sql import func
from flask import flash, redirect, url_for, request, jsonify, make_response
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from forms import TaskEditForm
from utils.html_element import colorize, button
from utils.formatter import format_thumbnail, format_account_action,\
    format_room_action, format_room_status, format_user_action, prop_name, prop_type, format_value, ts_to_time
from models import db, AppUser, UserProperty, Feedback, GiftGiving, WithdrawHistory, Payment
from config import IMAGE_DIR, IMAGE_BASE_PATH, TASK_CONFIG, PAGE_SIZE


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

    list_template = "user/user_view.html"

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
            "format_value": format_value,
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

        self.allowed_extensions = ('gif', 'jpg', 'jpeg', 'png', 'tiff')
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

    def is_file_allowed(self, filename):
        if not self.allowed_extensions:
            return True

        return ('.' in filename and
                filename.rsplit('.', 1)[1].lower() in
                map(lambda x: x.lower(), self.allowed_extensions))

    @staticmethod
    def is_file_exists(file_url):
        if not file_url:
            return False
        path = file_url.replace(IMAGE_BASE_PATH, "", 1).replace("/", os.sep)
        if path.startswith(os.sep):
            path = path[1:]
        return os.path.exists(os.path.join(IMAGE_DIR, path))

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
        form.img_url = task["img"]
        form.display.data = task["display"]
        form.task_type.data = task["task_type"].lower()
        form.help_msg = u"仅支持 gif, jpg, jpeg, png, tiff 格式"

        vc_str = json.dumps(self.vc_options, ensure_ascii=False)
        prop_str = json.dumps(self.prop_options, ensure_ascii=False)

        return self.render("user/task_edit.html", form=form, action=url_for('.edit_task', task_id=task_id), vc_options=vc_str, prop_options=prop_str)

    @expose('/edit/<task_id>', methods=["POST",])
    def edit_task(self, task_id):
        form = TaskEditForm()
        if not form.validate_on_submit():
            flash(u"缺少关键信息", category="error")
            return redirect(url_for('.task_edit_view', task_id=task_id))

        form_data = request.form

        if not self.is_file_exists(form_data["img_url"]):
            flash(u"请先上传图片", category="error")
            return redirect(url_for('.task_edit_view', task_id=task_id))

        with open(TASK_CONFIG) as f:
            task_info = json.load(f)
            for task in task_info:
                if task.get("task_id") == task_id:
                    task["task"] = form_data["task_name"]
                    task["img"] = form_data["img_url"]
                    task["task_type"] = form_data["task_type"]
                    task["task_desc"] = form_data["task_desc"]
                    task["display"] = form_data["display"]
                    task["prize"] = ":".join([form_data["award_type"], form_data["award_currency"], form_data["award_amount"]])
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

        return self.render("user/task_edit.html", form=form, action=url_for('.create_task'), vc_options=vc_str, prop_options=prop_str)

    @expose('/create', methods=('POST',))
    def create_task(self):
        form = TaskEditForm()
        if not form.validate_on_submit():
            flash(u"信息有误或缺失", category="error")
            return redirect(url_for('.create_task_view'))

        form_data = request.form

        if not self.is_file_exists(form_data["img_url"]):
            flash(u"请先上传图片", category="error")
            return redirect(url_for('.create_task_view'))

        with open(TASK_CONFIG) as f:
            task_info = json.load(f)

            task_info.append(
                {
                    "task_type": form_data["task_type"],
                    "task_id": str(len(task_info) + 1),
                    "img": form_data["img_url"],
                    "task": form_data["task_name"],
                    "task_desc": form_data["task_desc"],
                    "display": form_data["display"],
                    "prize": ":".join([form_data["award_type"], form_data["award_currency"], form_data["award_amount"]])
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

    @expose('/image/upload', methods=['POST',])
    def image_upload(self):
        img = request.files.get("img")
        if img is not None:
            if self.is_file_allowed(img.filename):
                try:
                    image = Image.open(img)
                except Exception:
                    return make_response(u"错误文件格式", 400)

                img_format = image.format.lower()
                if img_format in self.allowed_extensions:
                    imgbyte = image.tobytes()

                    md5 = hashlib.md5()
                    md5.update(imgbyte)
                    hash_str = md5.hexdigest()

                    path = os.path.join(IMAGE_DIR, hash_str[:4], hash_str[4:8])
                    img_path = os.path.join(path, hash_str[8:] + '.' + img_format)
                    if not os.path.exists(path):
                        os.makedirs(path)

                    image.save(img_path)
                else:
                    return make_response(u"文件格式错误", 400)
            else:
                return make_response(u"文件格式错误", 400)
        else:
            return make_response(u"文件不能为空", 400)

        return make_response(
            jsonify(
                {"img_url": "/".join([IMAGE_BASE_PATH, hash_str[:4], hash_str[4:8], hash_str[8:] + '.' + img_format])}
            ), 200)


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
        "locked": lambda v, c, m, n: colorize(u"封停", "red") if m.locked else colorize(u"正常", "green"),
        "locked_time": lambda v, c, m, n: m.locked_time.strftime("%Y-%m-%d %H:%M:%S") if m.locked_time else None,
        "room.control_flag": format_room_status,
        "room.disable_time": lambda v, c, m, n: m.room.disable_time.strftime("%Y-%m-%d %H:%M:%S") if m.room and m.room.disable_time else None,
        "acc_action": format_account_action,
        "room_action": format_room_action
    }

    def is_accessible(self):
        return current_user.is_authenticated

    # TODO: send YX message
    @expose("/block/<uid>")
    def block_account(self, uid):
        user = AppUser.query.get(uid)
        user.locked = True
        user.locked_time = datetime.now()
        db.session.commit()
        flash(u"封停成功", category="warning")
        return redirect(url_for("account.index_view"))

    @expose("/unblock/<uid>")
    def unblock_account(self, uid):
        user = AppUser.query.get(uid)
        user.locked = False
        db.session.commit()
        flash(u"解封成功", category="info")
        return redirect(url_for("account.index_view"))

    @expose("/room/suspend/<uid>")
    def suspend_room(self, uid):
        user = AppUser.query.get(uid)
        user.room.control_flag = 1
        db.session.commit()
        flash(u"勒令整改成功", category="warning")
        return redirect(url_for("account.index_view"))

    @expose("/room/block/<uid>")
    def block_room(self, uid):
        user = AppUser.query.get(uid)
        user.room.enable = False
        user.room.control_flag = 0
        user.room.disable_time = datetime.now()
        db.session.commit()
        flash(u"封停成功", category="warning")
        return redirect(url_for("account.index_view"))

    @expose("/room/unblock/<uid>")
    def unblock_room(self, uid):
        user = AppUser.query.get(uid)
        user.room.enable = True
        db.session.commit()
        flash(u"解封成功", category="info")
        return redirect(url_for("account.index_view"))