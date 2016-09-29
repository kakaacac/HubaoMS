# -*- coding: utf-8 -*-

from flask import flash, redirect, url_for, request, jsonify, make_response
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from utils.formatter import format_thumbnail, format_compere_action, prop_name, prop_type, format_value
from models import GiftGiving, db, AppUser, UserCertification, Compere, RoomStat
from config import PAGE_SIZE

class CompereView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

    column_auto_select_related = True
    column_list = ("uid", "rid", "user.cert.nickname", "user.display_name", "tags", "image", "description",
                   "user.level", "actions")
    column_default_sort = "uid"
    column_searchable_list = ("uid", "rid", "user.cert.nickname", "user.display_name")
    column_sortable_list = ("uid", "rid", "user.cert.nickname", "user.display_name", "tags", "user.level")
    column_labels = {
        "uid": u"主播 ID",
        "rid": u"房间 ID",
        "user.cert.nickname": u"登录名",
        "user.display_name": u"主播昵称",
        "tags": u"标签",
        "image": u"宣传图",
        "description": u"个人描述",
        "user.level": u"等级",
        "actions": u"其他信息"
    }
    column_formatters = {
        "image": format_thumbnail("image"),
        "actions": format_compere_action
    }

    list_template = "compere/compere_view.html"

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/income/<compere_id>')
    def income(self, compere_id):
        def pager_url(p):
            return url_for(".income", page=p+1, compere_id=compere_id)

        page = int(request.args.get("page", 1))
        records = GiftGiving.query.\
            filter_by(compere_id=compere_id).\
            join(AppUser, GiftGiving.uid == AppUser.uid).\
            join(UserCertification, GiftGiving.uid == UserCertification.uid).\
            with_entities(GiftGiving.id, UserCertification.nickname, AppUser.display_name,
                          GiftGiving.prop_id, GiftGiving.qty, GiftGiving.value, GiftGiving.currency,
                          GiftGiving.send_time).\
            paginate(page, PAGE_SIZE, False)

        kwargs = {
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

        return self.render("compere/income_detail.html", **kwargs)

    @expose('/other_info/<compere_id>')
    def other_info(self, compere_id):
        stat = RoomStat.query.join(Compere, Compere.rid == RoomStat.rid).filter(Compere.uid == compere_id).first()

        kwargs = {
            "room_id": stat.rid,
            "following": stat.,
            "level": user.level,
            "exp": user.exp,
            "vip": u"是" if user.vip else u"否",
            "amber": db.session.query(func.sum(GiftGiving.value)).filter_by(compere_id=uid, currency="vcy").one()[0] or 0
        }
        return self.render("user/user_extra_info.html", **kwargs)