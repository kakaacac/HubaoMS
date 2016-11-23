# -*- coding: utf-8 -*-
import json
from flask import flash, url_for, request
from flask_admin import expose

from base import AuthenticatedModelView, AuthenticatedBaseView
from models import Banner, db, AppUser, Room, UserCertification
from utils.formatter import format_thumbnail, format_banner_actions
from forms import BannerEditForm
from utils.functions import is_file_exists, json_response, abs_redirect
from config import PROPS_CONFIG

class BannerView(AuthenticatedModelView):
    column_list = ("id", "room_id", "room.name", "image", "login_name", "compere.display_name",
                   "position", "flag", "actions")
    column_default_sort = "id"
    column_searchable_list = ("room_id", "room.name", "login_name", "compere.display_name")
    column_sortable_list = ("room_id", "position", "flag")
    column_labels = {
        "id": u"ID",
        "room_id": u"房间 ID",
        "room.name": u"房间名",
        "image": u"宣传图片",
        "login_name": u"主播登录名",
        "compere.display_name": u"主播昵称",
        "position": u"位置",
        "flag": u"类型",
        "actions": u"操作"
    }
    column_formatters = {
        "image": format_thumbnail("image"),
        "actions": format_banner_actions,
        "flag": lambda v, c, m, n: u"网页" if m.flag == "web" else u"普通",
        "position": lambda v, c, m, n: {0: u"首页", 1: u"互动", 2: u"热播"}.get(m.position, 0)
    }

    list_template = "content/banner_view.html"

    @expose('/detail/<id>')
    def other_info(self, id):
        banner = Banner.query.get_or_404(id)

        kwargs = {
            "id": banner.id,
            "img_url": banner.image,
            "type": banner.flag,
            "redirect_url": banner.url,
        }
        return self.render("content/banner_extra_info.html", **kwargs)

    @expose('/delete/<id>')
    def delete(self, id):
        banner = Banner.query.get_or_404(id)
        db.session.delete(banner)
        db.session.commit()
        flash(u"删除轮播图成功", category="success")
        return abs_redirect(".index_view", **request.args)

    @expose('/edit/<id>')
    def banner_edit_view(self, id):
        banner = Banner.query.get_or_404(id)
        form = BannerEditForm()

        form.room_id.data = banner.room_id
        form.room_name.data = banner.room_name
        form.compere_id.data = banner.compere_uuid
        form.login_name.data = banner.login_name
        form.img_url.data = banner.image
        form.position.data = banner.position

        return self.render("content/banner_edit.html",
                           form=form,
                           action=url_for('.edit_banner', id=id),
                           cancel=url_for('.index_view'),
                           query_info=url_for('.query_info'),
                           title=u'修改轮播图')

    @expose('/edit/<id>', methods=['POST',])
    def edit_banner(self, id):
        banner = Banner.query.get_or_404(id)
        form = BannerEditForm()

        if not form.validate_on_submit():
            flash(u"信息有误或缺失", category="error")
            return abs_redirect('.banner_edit_view', id=id)

        if not is_file_exists(form.img_url.data):
            flash(u"请先上传图片", category="error")
            return abs_redirect('.banner_edit_view', id=id)

        banner.room_id = form.room_id.data
        banner.room_name = form.room_name.data
        banner.compere_uuid = form.compere_id.data
        banner.login_name = form.login_name.data
        banner.image = form.img_url.data
        banner.position = form.position.data
        banner.flag = form.banner_type.data

        if form.banner_type.data == 'web':
            banner.url = form.redirect_url.data

        user = AppUser.query.filter_by(uuid=form.compere_id.data).first()
        banner.compere_id = user.uid

        db.session.commit()

        flash(u"修改轮播图成功", category="success")
        return abs_redirect(".index_view", **request.args)

    @expose('/query')
    def query_info(self):
        query_key = request.args.get("type")
        query_value = request.args.get("value")

        if query_key not in ("room_id", "login_name"):
            return json_response({"error_msg": u"不支持该查询方法"}, 200)

        if not query_value:
            return json_response({
                "error_msg": u"房间 ID不能为空" if query_key == "room_id" else u"主播登录名不能为空"
            }, 200)

        if query_key == "room_id":
            compere = AppUser.query.\
                join(Room, Room.uid == AppUser.uid).\
                join(UserCertification, UserCertification.uid == AppUser.uid).\
                filter(Room.rid == int(query_value)).\
                with_entities(Room.rid, Room.name, AppUser.uuid, UserCertification.nickname).first()
        else:
            compere = AppUser.query.\
                join(Room, Room.uid == AppUser.uid).\
                join(UserCertification, UserCertification.uid == AppUser.uid).\
                filter(UserCertification.nickname == query_value).\
                with_entities(Room.rid, Room.name, AppUser.uuid, UserCertification.nickname).first()

        if not compere:
            return json_response({
                "error_msg": u"主播不存在"
            }, 200)

        return json_response({
            "room_id": compere.rid,
            "room_name": compere.name,
            "compere_id": compere.uuid.replace("-", ""),
            "login_name": compere.nickname
        }, 200)

    @expose('/create')
    def create_banner_view(self):
        form = BannerEditForm()

        return self.render("content/banner_edit.html",
                           form=form,
                           action=url_for('.create_banner'),
                           cancel=url_for('.index_view'),
                           query_info=url_for('.query_info'),
                           title=u'添加轮播图')

    @expose('/create', methods=['POST',])
    def create_banner(self):
        banner = Banner()
        form = BannerEditForm()

        if not form.validate_on_submit():
            flash(u"信息有误或缺失", category="error")
            return abs_redirect('.create_banner_view')

        if not is_file_exists(form.img_url.data):
            flash(u"请先上传图片", category="error")
            return abs_redirect('.create_banner_view')

        banner.room_id = form.room_id.data
        banner.room_name = form.room_name.data
        banner.compere_uuid = form.compere_id.data
        banner.login_name = form.login_name.data
        banner.image = form.img_url.data
        banner.position = form.position.data
        banner.flag = form.banner_type.data

        if form.banner_type.data == 'web':
            banner.url = form.redirect_url.data

        user = AppUser.query.filter_by(uuid=form.compere_id.data).first()
        banner.compere_id = user.uid

        db.session.add(banner)
        db.session.commit()

        flash(u"添加轮播图成功", category="success")
        return abs_redirect(".index_view", **request.args)


class RoomTagsView(AuthenticatedModelView):
    can_create = True
    can_edit = True
    can_delete = True
    column_display_actions = True
    column_display_pk = True

    column_list = ("id", "name", "mode", "weight")
    column_default_sort = "id"
    column_sortable_list = ("mode", "weight")
    column_labels = {
        "id": u"ID",
        "name": u"标签名",
        "mode": u"模块",
        "weight": u"权重"
    }
    column_formatters = {
        "mode": lambda v, c, m, n: {1: u"个人", 2: u"互动"}.get(m.mode)
    }

    form_columns = ("id", "name", "mode", "weight")
    form_choices = {"mode": [("1", u"个人"), ("2", u"互动")]}


class GameConfigView(AuthenticatedBaseView):
    @expose()
    def index_view(self):
        return self.render("content/interactive_game_config.html")


class PropsView(AuthenticatedBaseView):
    @staticmethod
    def load_props_config():
        with open(PROPS_CONFIG) as f:
            return json.load(f)

    @expose()
    def props_list(self):
        props = []
        for item in self.load_props_config()["prop_info"]:
            if int(item["prop_id"]) > 1000:
                currency, value = item["value"].split(":")
                item.update({"currency": currency, "value":float(value)})
                props.append(item)

        return self.render("content/props_view.html", data=props)




