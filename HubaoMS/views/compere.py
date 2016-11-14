# -*- coding: utf-8 -*-
import time
from flask import flash, redirect, url_for, request
from flask_admin import expose

from base import AuthenticatedBaseView, AuthenticatedModelView
from utils.formatter import format_thumbnail, format_compere_action, prop_name, prop_type, format_receive_value,\
    format_verification_status, format_verification_actions, format_time, format_withdrawal_status,\
    format_withdrawal_actions, format_withdrawal_amount
from models import GiftGiving, db, AppUser, UserCertification, Compere, RoomStat, CompereVerification, WithdrawHistory
from config import PAGE_SIZE
from forms import CompereConfigurationForm
from utils import redis


class CompereView(AuthenticatedModelView):
    column_auto_select_related = True
    column_list = ("uid", "rid", "user.cert.nickname", "user.display_name", "image", "description",
                   "user.level", "actions")
    column_default_sort = "uid"
    column_searchable_list = ("uid", "rid", "user.cert.nickname", "user.display_name")
    column_sortable_list = ("uid", "rid", "user.cert.nickname", "user.display_name", "tags", "user.level")
    column_labels = {
        "uid": u"主播 ID",
        "rid": u"房间 ID",
        "user.cert.nickname": u"登录名",
        "user.display_name": u"主播昵称",
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
            "format_value": format_receive_value,
            "prop_type": prop_type,
            "num_pages": records.pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": PAGE_SIZE,
            "total": records.total,
            "uid": compere_id
        }

        return self.render("compere/income_detail.html", **kwargs)

    @expose('/other_info/<compere_id>')
    def other_info(self, compere_id):
        stat = RoomStat.query.join(Compere, Compere.rid == RoomStat.rid).filter(Compere.uid == compere_id).first()

        kwargs = {
            "room_id": stat.rid,
            "audience": stat.num_audience,
            "follower": stat.num_follows,
            "num_lives": stat.num_live,
            "popularity": stat.num_popularity,
            "likes": stat.num_likes
        }
        return self.render("compere/compere_extra_info.html", **kwargs)


class CompereVerificationView(AuthenticatedModelView):
    column_list = ("uid", "real_name", "user.cert.nickname", "card_id", "bankcard_no", "id_card_front", "id_card_back",
                   "phtot_in_hand", "commit_time", "status", "actions")
    column_default_sort = "uid"
    column_searchable_list = ("uid", "real_name", "user.cert.nickname", "card_id")
    column_sortable_list = ("uid", "user.cert.nickname", "commit_time", "status")
    column_labels = {
        "uid": u"主播 ID",
        "real_name": u"真实姓名",
        "user.cert.nickname": u"登录名",
        "card_id": u"身份证号",
        "bankcard_no": u"银行卡号",
        "id_card_front": u"身份证正面",
        "id_card_back": u"身份证反面",
        "phtot_in_hand": u"手持照片",
        "commit_time": u"提交时间",
        "status": u"审核状态",
        "actions": u"操作"
    }

    column_formatters = {
        "status": format_verification_status,
        "id_card_front": format_thumbnail("id_card_front"),
        "id_card_back": format_thumbnail("id_card_back"),
        "phtot_in_hand": format_thumbnail("phtot_in_hand"),
        "commit_time": lambda v, c, m, n: m.commit_time.strftime("%Y-%m-%d %H:%M:%S"),
        "actions": format_verification_actions
    }

    list_template = "compere/compere_verification_view.html"

    @expose('/<vid>/accept')
    def verification_pass(self, vid):
        ver = CompereVerification.query.get_or_404(vid)
        ver.status = True
        db.session.commit()
        flash(u"审核已通过", category="info")
        return redirect(url_for(".index_view"))

    @expose('/<vid>/reject')
    def verification_fail(self, vid):
        ver = CompereVerification.query.get_or_404(vid)
        ver.status = False
        db.session.commit()
        flash(u"审核已拒绝", category="warning")
        return redirect(url_for(".index_view"))


class Withdrawal(AuthenticatedModelView):
    column_list = ("id", "uid", "user.cert.nickname", "amount", "vfc_amount", "vcy_amount", "apply_time",
                   "deal_time", "status", "actions")
    column_default_sort = "id"
    column_searchable_list = ("uid", "user.cert.nickname")
    column_sortable_list = ("uid", "user.cert.nickname", "amount", "vfc_amount", "vcy_amount", "apply_time",
                            "deal_time", "status")
    column_labels = {
        "id": u"ID",
        "uid": u"用户 ID",
        "user.cert.nickname": u"登录名",
        "amount": u"提现金额",
        "vfc_amount": u"提现小草",
        "vcy_amount": u"提现琥珀",
        "apply_time": u"申请时间",
        "deal_time": u"处理时间",
        "status": u"申请状态",
        "actions": u"操作"
    }

    column_formatters = {
        "status": format_withdrawal_status,
        "apply_time": format_time("apply_time"),
        "deal_time": format_time("deal_time"),
        "amount": format_withdrawal_amount,
        "actions": format_withdrawal_actions
    }

    @expose('/<wid>/accept')
    def withdrawal_pass(self, wid):
        wd = WithdrawHistory.query.get_or_404(wid)
        wd.status = 2
        db.session.commit()
        flash(u"提现申请已通过", category="info")
        return redirect(url_for(".index_view"))

    @expose('/<wid>/reject')
    def withdrawal_fail(self, wid):
        wd = WithdrawHistory.query.get_or_404(wid)
        wd.status = 3
        wd.deal_time = int(time.time())
        db.session.commit()
        flash(u"提现申请已拒绝", category="warning")
        return redirect(url_for(".index_view"))


class CompereConf(AuthenticatedBaseView):
    @expose(methods=['GET', 'POST'])
    def compere_configuration(self):
        form = CompereConfigurationForm()
        if request.method == "POST":
            redis.master().hset('conf','check_required', "true" if form.conf.data == "1" else "false")
            flash(u"修改成功", category="info")
            return redirect(url_for(".compere_configuration"))
        else:
            check = redis.slave().hget('conf','check_required')
            return self.render("compere/compere_conf.html",
                               form=form,
                               action=url_for(".compere_configuration"),
                               check_required=(check.lower() == "true"))