# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Markup, url_for

from html_element import colorize, button


def prop_name(pid):
    return pid


def format_value(v, c):
    t = u"骨头" if c == "vcy" else u"小草"
    return u"{}{}".format(v, t)


def prop_type(c):
    return u"收费道具" if c == "vcy" else u"免费道具"


ts_to_time = lambda ts: datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def format_thumbnail(attr):
    def thumbnail(view, context, model, name):
        img = getattr(model, attr)
        if not img:
            return ''

        return Markup(u'<a class="shade-btn" href="javascript:;" data-src="%s">'
                      u'<img src="%s" width="40" height="40" title="点击放大"></a>' % (img, img))
    return thumbnail


def format_room_status(view, context, model, name):
    if model.room:
        if model.room.enable:
            if model.room.control_flag == 0:
                return colorize(u"正常", "green")
            else:
                return colorize(u"整改中", "#aa6708")
        else:
            return colorize(u"封停", "red")
    else:
        return u"没有直播间"


def format_account_action(view, context, model, name):
    if model.locked:
        return button([(u"解封", url_for("account.unblock_account", uid=model.uid))])
    else:
        return button([(u"封停", url_for("account.block_account", uid=model.uid))])


def format_room_action(view, context, model, name):
    if model.room:
        if model.room.enable:
            if model.room.control_flag == 0:
                return button([(u"封停", url_for("account.block_room", uid=model.uid)),
                               (u"整改", url_for("account.suspend_room", uid=model.uid))])
            else:
                return button([(u"封停", url_for("account.block_room", uid=model.uid))])
        else:
            return button([(u"解封", url_for("account.unblock_room", uid=model.uid))])


def format_user_action(view, context, model, name):
    return button([
        (u"送礼", url_for("user.gift_giving_detail", uid=model.uid)),
        (u"充值", url_for("user.recharge_detail", uid=model.uid)),
        (u"资产", url_for("user.property_info", uid=model.uid)),
        (u"其他", url_for("user.other_info", uid=model.uid)),
    ], btn_class="btn btn-default btn-sm")


def format_compere_action(view, context, model, name):
    return button([
        (u"收益", url_for("compere.income", compere_id=model.uid)),
        (u"其他", url_for("compere.other_info", compere_id=model.uid)),
    ], btn_class="btn btn-default btn-sm")