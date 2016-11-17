# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Markup, url_for, request

from html_element import colorize, button
from utils import redis

def prop_name(pid):
    return pid


def format_present_value(v, c):
    t = u"骨头" if c == "vcy" else u"小草"
    return u"{}{}".format(v, t)


def format_receive_value(v, c):
    t = u"琥珀" if c == "vcy" else u"小草"
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


def format_account_status(view, context, model, name):
    if model.locked:
        expire = redis.slave().hget("control:block:account", model.uuid.replace("-", ""))
        return colorize(u"封停到 {}".format(expire), "red") if expire else colorize(u"封停", "red")
    else:
        return colorize(u"正常", "green")


def format_room_status(view, context, model, name):
    if model.room:
        if model.room.enable:
            if model.room.control_flag == 0:
                return colorize(u"正常", "green")
            else:
                return colorize(u"整改中", "#aa6708")
        else:
            expire = redis.slave().hget("control:block:room", model.room.rid)
            return colorize(u"封停到 {}".format(expire), "red") if expire else colorize(u"封停", "red")
    else:
        return u"没有直播间"


def format_account_action(view, context, model, name):
    if model.locked:
        return button([(u"解封", url_for("account.unblock_account", uid=model.uid, **request.args))])
    else:
        return button([(u"封停", url_for("account.block_account", uid=model.uid, **request.args))]) + \
               Markup(u'<a tabindex="0" class="btn btn-default account-block" role="button" '
                      u'data-toggle="popover" title="选择时间" data-action="{}">定时封停</a>'.
                      format(url_for("account.temporary_block_account", uid=model.uid, **request.args)))


def format_room_action(view, context, model, name):
    if model.room:
        if model.room.enable:
            if model.room.control_flag == 0:
                return button([(u"封停", url_for("account.block_room", rid=model.room.rid, **request.args))]) + \
                       Markup(u'<a tabindex="0" class="btn btn-default room-block" role="button" '
                              u'data-toggle="popover" title="选择时间" data-action="{}">定时封停</a>'.
                              format(url_for("account.temporary_block_room", rid=model.room.rid, **request.args))) + \
                       button([(u"整改", url_for("account.suspend_room", rid=model.room.rid, **request.args))])
            else:
                return button([(u"封停", url_for("account.block_room", rid=model.room.rid, **request.args))]) + \
                       Markup(u'<a tabindex="0" class="btn btn-default room-block" role="button" '
                              u'data-toggle="popover" title="选择时间" data-action="{}">定时封停</a>'.
                              format(url_for("account.temporary_block_room", rid=model.room.rid, **request.args)))
        else:
            return button([(u"解封", url_for("account.unblock_room", rid=model.room.rid, **request.args))])


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


def format_verification_status(view, context, model, name):
    if model.status is not None:
        return colorize(u"审核通过", "green") if model.status else colorize(u"审核失败", "#c55")
    return u"未审核"


def format_verification_actions(view, context, model, name):
    return button([
        (u'<span class="glyphicon glyphicon-ok" title="通过"></span>',
         url_for("verification.verification_pass", vid=model.ccid, **request.args), 'pass-btn'),
        (u'<span class="glyphicon glyphicon-remove" title="拒绝"></span>',
         url_for("verification.verification_fail", vid=model.ccid, **request.args), 'reject-btn')
    ], btn_class="", vertical=True) if model.status is None else ""


def format_withdrawal_status(view, context, model, name):
    return {
        1: u"审核中",
        2: colorize(u"提现成功", "green"),
        3: colorize(u"提现失败", "#c55"),
        4: colorize(u"自动兑换", "orange")
    }.get(model.status)


def format_withdrawal_actions(view, context, model, name):
    return button([
        (u'<span class="glyphicon glyphicon-ok" title="同意"></span>',
         url_for("withdrawal.withdrawal_pass", wid=model.id, **request.args), 'pass-btn'),
        (u'<span class="glyphicon glyphicon-remove" title="拒绝"></span>',
         url_for("withdrawal.withdrawal_fail", wid=model.id, **request.args), 'reject-btn')
    ], btn_class="", vertical=True) if model.status == 1 else ""


def format_banner_actions(view, context, model, name):
    return button([
        (u'<span class="glyphicon glyphicon-eye-open" style="margin: 0 2px;" title="其他信息"></span>',
         url_for("banner.other_info", id=model.id)),
        (u'<span class="glyphicon glyphicon-pencil" style="margin: 0 2px;" title="修改"></span>',
         url_for("banner.banner_edit_view", id=model.id)),
        (u'<span class="glyphicon glyphicon-trash" style="margin: 0 2px;" title="删除"></span>',
         url_for("banner.delete", id=model.id), "delete-btn"),
    ], btn_class="")


def format_time(attr):
    return lambda view, context, model, name: ts_to_time(getattr(model, attr)) if getattr(model, attr) else ""


def format_withdrawal_amount(view, context, model, name):
    return u"{} 骨头".format(model.amount) if model.status == 4 else model.amount


def format_room_actions(view, context, model, name):
    pass


def format_room_channel(view, context, model, name):
    return u"互动热播" if model.game_id is not None else u"个人热播"


def format_boolean(attr, true_color=None, false_color=None):
    attr_path = attr.split(".")
    def f(view, context, model, name):
        try:
            attribute = getattr(model, attr_path[0])
            if len(attr_path) > 1:
                for a in attr_path[1:]:
                    attribute = getattr(attribute, a)
        except AttributeError:
            return ""
        if isinstance(attribute, bool):
            if attribute:
                return colorize(u"是", true_color) if true_color else u"是"
            else:
                return colorize(u"否", false_color) if false_color else u"否"
        else:
            raise Exception("Cannot format non-boolean type attribute")
    return f


def format_broadcast_range(view, context, model, name):
    if model.broadcast_range == "tag":
        return u"标签"
    elif model.broadcast_range == "specified":
        return u"指定"
    else:
        return u"全部"


def format_broadcast_status(view, context, model, name):
    if not model.interrupted:
        now = datetime.now()
        if model.end_time >= now:
            return colorize(u"进行中", "green") if model.start_time < now else colorize(u"等待中", "orange")
    return u"已停止"


def format_broadcast_actions(view, context, model, name):
    if model.end_time >= datetime.now():
        if model.interrupted:
            return button([
                (u"修改", url_for("broadcast.edit_broadcast_view", id=model.id)),
                (u"重新启动", url_for("broadcast.restart_broadcast", id=model.id, **request.args), 'restart-btn'),
            ], btn_class="btn btn-default btn-sm")
        else:
            return button([
                (u"修改", url_for("broadcast.edit_broadcast_view", id=model.id)),
                (u"停止", url_for("broadcast.stop_broadcast", id=model.id, **request.args), 'stop-btn'),
            ], btn_class="btn btn-default btn-sm")
    return ""


def format_live_stat_actions(view, context, model, name):
    return button([
        (u'<span class="glyphicon glyphicon-list-alt" title="开播列表"></span>',
         url_for("show_statistics.stream_list", id=model.id)),
    ], btn_class="")


def format_gift_stat_detail(role):
    assert role in ["presenter", "recipient"]
    title = u"赠礼" if role == "presenter" else u"收礼"
    def f(view, context, model, name):
        return button([
            (u'<span class="glyphicon glyphicon-list-alt" '
             u'title="{}列表"></span>'.format(title),
             url_for("gift_statistics.{}_list".format(role), id=model.id))], btn_class="")
    return f