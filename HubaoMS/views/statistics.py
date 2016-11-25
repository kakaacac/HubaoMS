# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
import time
from collections import OrderedDict
from flask import request, url_for
from flask_admin import expose
from sqlalchemy.sql import func, and_, not_, expression

from base import AuthenticatedModelView, AuthenticatedBaseView
from models import LiveStreamHistory, DailyStatistics, GameStat, GiftGiving, AppUser, UserCertification, Refund, db, \
    Room, Device
from config import ROBOT_APP_ID
from utils.formatter import format_live_stat_actions, format_gift_stat_detail
from utils.functions import num_of_page


class LiveShowStatView(AuthenticatedModelView):
    column_list = ("processing_date", "new_compere", "active_compere", "total_compere", "total_show", "normal_show",
                   "paid_show", "interactive_show", "actions")
    column_default_sort = ("processing_date", True)
    column_searchable_list = ("processing_date",)
    column_sortable_list = ("processing_date", "new_compere", "active_compere", "total_compere",
                            "normal_show", "paid_show", "interactive_show")
    column_labels = {
        "processing_date": u"日期",
        "new_compere": u"新增主播",
        "active_compere": u"当日活跃主播",
        "total_compere": u"总活跃主播",
        "total_show": u"总直播数",
        "normal_show": u"普通直播",
        "paid_show": u"付费直播",
        "interactive_show": u"互动直播",
        "actions": u"开播列表"
    }

    column_formatters = {
        "processing_date": lambda v, c, m, n: m.processing_date.strftime("%Y-%m-%d"),
        "total_show": lambda v, c, m, n: m.normal_show + m.paid_show,
        "actions": format_live_stat_actions
    }

    extra_sorting = {
        "total_show": "normal_show + paid_show"
    }

    @expose('/list/<id>')
    def stream_list(self, id):
        stat = DailyStatistics.query.get_or_404(id)
        page = int(request.args.get("page", 1))

        shows = LiveStreamHistory.query.\
            join(UserCertification, LiveStreamHistory.uid == UserCertification.uid).\
            with_entities(UserCertification.nickname, LiveStreamHistory.rid, LiveStreamHistory.start_time,
                          LiveStreamHistory.close_time, LiveStreamHistory.max_audience,
                          LiveStreamHistory.total_audience, LiveStreamHistory.type,
                          LiveStreamHistory.close_time - LiveStreamHistory.start_time).\
            filter(stat.processing_date == func.date(LiveStreamHistory.start_time)).\
            order_by(LiveStreamHistory.start_time, LiveStreamHistory.rid).\
            paginate(page, self.page_size, False)

        show_type = LiveStreamHistory.query.\
            with_entities(LiveStreamHistory.rid, func.count(GameStat.game_start)).\
            filter(stat.processing_date == func.date(LiveStreamHistory.start_time)).\
            outerjoin(GameStat,
                      and_(LiveStreamHistory.rid == GameStat.room_id,
                           LiveStreamHistory.start_time <= GameStat.game_start,
                           LiveStreamHistory.close_time >= GameStat.game_end)).\
            group_by(LiveStreamHistory.start_time, LiveStreamHistory.rid).\
            order_by(LiveStreamHistory.start_time, LiveStreamHistory.rid).\
            paginate(page, self.page_size, False)

        gifts = LiveStreamHistory.query.\
            with_entities(LiveStreamHistory.rid, func.sum(GiftGiving.value)).\
            outerjoin(GiftGiving,
                      and_(LiveStreamHistory.uid == GiftGiving.compere_id,
                           LiveStreamHistory.start_time <= GiftGiving.send_time,
                           LiveStreamHistory.close_time >= GiftGiving.send_time,
                           GiftGiving.prop_id < 1000,
                           GiftGiving.currency == 'vcy')).\
            outerjoin(AppUser, GiftGiving.uid == AppUser.uid).\
            outerjoin(Device, and_(AppUser.active_device == Device.device_id,
                                   not_(Device.device_info["app_id"].astext.in_(ROBOT_APP_ID)))).\
            filter(stat.processing_date == func.date(LiveStreamHistory.start_time)).\
            group_by(LiveStreamHistory.start_time, LiveStreamHistory.rid).\
            order_by(LiveStreamHistory.start_time, LiveStreamHistory.rid).\
            paginate(page, self.page_size, False)

        data = zip(*(zip(*shows.items) + zip(*show_type.items) + zip(*gifts.items)))

        zero_duration = timedelta()

        data = [{
            "id": str(item[1]) + str(int(time.mktime(item[2].timetuple()))) + "{:06d}".format(item[2].microsecond),
            "login_name": item[0],
            "room_id": item[1],
            "start_time": item[2].strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": item[3].strftime("%Y-%m-%d %H:%M:%S") if item[3] else u"直播中",
            "max_audience": item[4] or 0,
            "total_audience": item[5] or 0,
            "type": item[6],
            "duration": (str(item[7] - timedelta(microseconds=item[7].microseconds))
                         if item[7] > zero_duration else str(zero_duration)) if item[7] else u"直播中",
            "interactive": item[9] > 0,
            "income": item[11] or 0
                } for item in data]

        def pager_url(p):
            return url_for(".stream_list", page=p+1, id=id)

        kwargs = {
            "data": data,
            "num_pages": shows.pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": self.page_size,
            "total": shows.total,
            "date": stat.processing_date.strftime("%Y-%m-%d")
        }

        return self.render("statistics/live_stream_list.html", **kwargs)

    @expose('/detail/<id>')
    def stream_detail(self, id):
        room_id = int(id[:5])
        ts = int(id[5:15])
        microsec = int(id[15:])
        start_time = datetime.fromtimestamp(ts)
        start_time = start_time.replace(microsecond=microsec)

        streams = LiveStreamHistory.query.\
            filter(LiveStreamHistory.rid == room_id, LiveStreamHistory.start_time >= start_time).\
            join(AppUser, AppUser.uid == LiveStreamHistory.uid).\
            with_entities(AppUser.uuid, LiveStreamHistory).order_by(LiveStreamHistory.start_time).limit(2).all()
        if len(streams) == 2:
            stream, next_stream = streams
        else:
            stream = streams[0]
            next_stream = None

        if stream[1].close_time:
            duration = stream[1].close_time - stream[1].start_time
            duration -= timedelta(microseconds=duration.microseconds)

            refund_limit = max(stream[1].close_time + timedelta(seconds=1), next_stream[1].close_time) if next_stream \
                else stream[1].close_time + timedelta(seconds=1)
        else:
            duration = "-1"
            refund_limit = datetime.now()

        interactives = GameStat.query.filter(GameStat.room_id == room_id, GameStat.game_start >= start_time)

        if stream[1].close_time:
            interactives = interactives.filter(GameStat.game_end <= stream[1].close_time)
        interactives = interactives.order_by(GameStat.game_start).all()

        # interactive games info
        is_interactive = len(interactives) > 0
        if is_interactive:
            interactives_info = {
                "duration": timedelta(),
                "compensation": {"vfc": 0, "vcy": 0},
                "consumption": {"vfc": 0, "vcy": 0},
                "count": {1: 0, 2: 0}
            }
            interactive_data = []

            for item in interactives:
                game_duration = item.game_end - item.game_start
                interactives_info["duration"] += game_duration
                interactives_info["consumption"][item.currency] += item.bet or 0
                interactives_info["compensation"][item.currency] += item.award + interactives_info["consumption"][item.currency]
                interactives_info["count"][item.game_id or 1] += 1

                interactive_data.append({
                    "start": item.game_start.strftime("%H:%M:%S"),
                    "end": item.game_end.strftime("%H:%M:%S"),
                    "duration": str(game_duration - timedelta(microseconds=game_duration.microseconds)),
                    "type": item.game_id,
                    "consumption": item.bet or 0,
                    "compensation": item.bet or 0 + item.award,
                    "currency": item.currency
                })

            interactives_info["duration"] -= timedelta(microseconds=interactives_info["duration"].microseconds)
            interactives_info["duration"] = str(interactives_info["duration"])
            interactives_info["count"] = [(k, v) for k, v in interactives_info["count"].iteritems() if v > 0]
        else:
            interactives_info = None
            interactive_data = None

        # ticket info
        is_paid = stream[1].type == 'paid'
        if is_paid:
            tickets = GiftGiving.query.filter(GiftGiving.compere_id == stream[1].uid,
                                              GiftGiving.send_time >= start_time,
                                              GiftGiving.prop_id >= 1000)

            if stream[1].close_time:
                tickets = tickets.filter(GiftGiving.send_time <= stream[1].close_time)

            tickets = tickets.with_entities(GiftGiving.currency, func.sum(GiftGiving.value)).\
                group_by(GiftGiving.currency).all()

            refunds = Refund.query.filter(Refund.compere_id == stream[0],
                                          Refund.refund_time >= start_time,
                                          Refund.refund_time <= refund_limit).\
                with_entities(Refund.currency, func.sum(Refund.value)).group_by(Refund.currency).all()

            ticket_info = {"vfc": 0, "vcy": 0}
            refund_info = {"vfc": 0, "vcy": 0}

            for item in tickets:
                ticket_info[item.currency] += item[1]

            for item in refunds:
                ticket_info[item.currency] -= item[1]
                refund_info[item.currency] += item[1]
        else:
            ticket_info = None
            refund_info = None

        kwargs = {
            "duration": str(duration),
            "is_interactive": is_interactive,
            "interactives_info": interactives_info,
            "interactive_data": interactive_data,
            "is_paid": is_paid,
            "ticket_info": ticket_info,
            "refund_info": refund_info,
            "room_id": room_id,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S")
        }

        return self.render("statistics/live_stream_detail.html", **kwargs)


class GiftStatView(AuthenticatedModelView):
    column_list = ("processing_date", "vfc_received", "vcy_received", "presenter_list", "recipient_list")
    column_default_sort = ("processing_date", True)
    column_searchable_list = ("processing_date",)
    column_sortable_list = ("processing_date", "vfc_received", "vcy_received")
    column_labels = {
        "processing_date": u"日期",
        "vfc_received": u"收取小草",
        "vcy_received": u"收取琥珀",
        "presenter_list": u"赠礼列表",
        "recipient_list": u"收礼列表"
    }

    column_formatters = {
        "processing_date": lambda v, c, m, n: m.processing_date.strftime("%Y-%m-%d"),
        "presenter_list": format_gift_stat_detail("presenter"),
        "recipient_list": format_gift_stat_detail("recipient")
    }

    list_template = "indexed_thumbnail_list.html"

    @expose('/presenter/<id>')
    def presenter_list(self, id):
        stat = DailyStatistics.query.get_or_404(id)
        page = int(request.args.get("page", 1))

        ALL = db.session.query(GiftGiving.uid, GiftGiving.currency, GiftGiving.value, GiftGiving.send_time).\
            filter(stat.processing_date == func.date(GiftGiving.send_time), GiftGiving.prop_id < 1000).cte("ALL")

        ALL_UID = db.session.query(ALL.c.uid).group_by(ALL.c.uid).order_by(func.min(ALL.c.send_time))

        UIDs = ALL_UID.offset((page - 1)*self.page_size).limit(self.page_size).subquery("UIDs")
        RESULT = db.session.query(ALL.c.uid, ALL.c.money_type, func.sum(ALL.c.t_price)).\
            join(UIDs, ALL.c.uid == UIDs.c.uid).group_by(ALL.c.uid, ALL.c.money_type).subquery("RESULT")
        DATA = db.session.query(RESULT).join(UserCertification, UserCertification.uid == RESULT.c.uid).\
            join(Room, Room.uid == RESULT.c.uid).\
            add_columns(Room.rid, UserCertification.nickname)

        count = ALL_UID.count()

        num_pages = num_of_page(count, self.page_size)

        data = OrderedDict()
        for item in DATA.all():
            if not data.has_key(item[0]):
                data[item[0]] = {"vfc": 0, "vcy": 0, "login_name": item[4], "room_id": item[3]}
            data[item[0]][item[1]] = item[2]

        result  = []
        for k, v in data.iteritems():
            d = {"user_id": k}
            d.update(v)
            result.append(d)

        def pager_url(p):
            return url_for(".presenter_list", page=p+1, id=id)

        kwargs = {
            "data": result,
            "num_pages": num_pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": self.page_size,
            "total": count,
            "title": u"赠礼列表 " + stat.processing_date.strftime("%Y-%m-%d"),
            "sid": id
        }
        return self.render("statistics/presenter_list.html", **kwargs)

    @expose('/recipient/<id>')
    def recipient_list(self, id):
        stat = DailyStatistics.query.get_or_404(id)
        page = int(request.args.get("page", 1))

        ALL = db.session.query(GiftGiving.compere_id, GiftGiving.currency, GiftGiving.value, GiftGiving.send_time).\
            filter(stat.processing_date == func.date(GiftGiving.send_time), GiftGiving.prop_id < 1000).cte("ALL")

        ALL_UID = db.session.query(ALL.c.compere_id).group_by(ALL.c.compere_id).order_by(func.min(ALL.c.send_time))

        UIDs = ALL_UID.offset((page - 1)*self.page_size).limit(self.page_size).subquery("UIDs")
        RESULT = db.session.query(ALL.c.compere_id, ALL.c.money_type, func.sum(ALL.c.t_price)).\
            join(UIDs, ALL.c.compere_id == UIDs.c.compere_id).group_by(ALL.c.compere_id, ALL.c.money_type).subquery("RESULT")
        DATA = db.session.query(RESULT).join(UserCertification, UserCertification.uid == RESULT.c.compere_id).\
            join(Room, Room.uid == RESULT.c.compere_id).\
            add_columns(Room.rid, UserCertification.nickname)

        count = ALL_UID.count()

        num_pages = num_of_page(count, self.page_size)

        data = OrderedDict()
        for item in DATA.all():
            if not data.has_key(item[0]):
                data[item[0]] = {"vfc": 0, "vcy": 0, "login_name": item[4], "room_id": item[3]}
            data[item[0]][item[1]] = item[2]

        result  = []
        for k, v in data.iteritems():
            d = {"user_id": k}
            d.update(v)
            result.append(d)

        def pager_url(p):
            return url_for(".presenter_list", page=p+1, id=id)

        kwargs = {
            "data": result,
            "num_pages": num_pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": self.page_size,
            "total": count,
            "title": u"收礼列表 " + stat.processing_date.strftime("%Y-%m-%d"),
            "sid": id
        }
        return self.render("statistics/recipient_list.html", **kwargs)

    @expose('/presenter/detail/<sid>/<uid>')
    def presenter_detail(self, sid, uid):
        stat = DailyStatistics.query.get(sid)
        user = UserCertification.query.filter_by(uid=uid).first()
        page = int(request.args.get("page", 1))

        records = GiftGiving.query.filter(stat.processing_date == func.date(GiftGiving.send_time),
                                          GiftGiving.prop_id < 1000,
                                          GiftGiving.uid == uid).\
            join(UserCertification, UserCertification.uid == GiftGiving.compere_id).\
            join(Room, Room.uid == GiftGiving.compere_id).order_by(GiftGiving.send_time).\
            with_entities(UserCertification.nickname, Room.rid,
                          GiftGiving.send_time, GiftGiving.currency, GiftGiving.value).\
            paginate(page, self.page_size, False)

        data = [{
            "login_name": item[0],
            "room_id": item[1],
            "send_time": item[2].strftime("%H:%M:%S"),
            "currency": item[3],
            "value": item[4]
        } for item in records.items]

        def pager_url(p):
            return url_for(".presenter_detail", page=p+1, sid=sid, uid=uid)

        kwargs = {
            "data": data,
            "num_pages": records.pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": self.page_size,
            "total": records.total,
            "title": u"{} {} 送礼记录".format(user.nickname, stat.processing_date.strftime("%Y-%m-%d"))
        }

        return self.render("statistics/presenter_detail.html", **kwargs)

    @expose('/recipient/detail/<sid>/<uid>')
    def recipient_detail(self, sid, uid):
        stat = DailyStatistics.query.get(sid)
        user = UserCertification.query.filter_by(uid=uid).first()
        page = int(request.args.get("page", 1))

        records = GiftGiving.query.filter(stat.processing_date == func.date(GiftGiving.send_time),
                                          GiftGiving.prop_id < 1000,
                                          GiftGiving.compere_id == uid).\
            join(UserCertification, UserCertification.uid == GiftGiving.uid).\
            join(Room, Room.uid == GiftGiving.uid).order_by(GiftGiving.send_time).\
            with_entities(UserCertification.nickname, Room.rid,
                          GiftGiving.send_time, GiftGiving.currency, GiftGiving.value).\
            paginate(page, self.page_size, False)

        data = [{
            "login_name": item[0],
            "room_id": item[1],
            "send_time": item[2].strftime("%H:%M:%S"),
            "currency": item[3],
            "value": item[4]
        } for item in records.items]

        def pager_url(p):
            return url_for(".recipient_detail", page=p+1, sid=sid, uid=uid)

        kwargs = {
            "data": data,
            "num_pages": records.pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": self.page_size,
            "total": records.total,
            "title": u"{} {} 收礼记录".format(user.nickname, stat.processing_date.strftime("%Y-%m-%d"))
        }

        return self.render("statistics/recipient_detail.html", **kwargs)


class InteractiveGameStatView(AuthenticatedBaseView):
    @staticmethod
    def update_item(dictionary, game_id, currency, award, bet):
        if game_id == 1:
            dictionary["dice_stat"]["consumption"][currency] = bet
            dictionary["dice_stat"]["compensation"][currency] = award + bet
        elif game_id == 2:
            dictionary["qna_stat"]["consumption"][currency] = bet
            dictionary["qna_stat"]["compensation"][currency] = award + bet

    def get_list(self):
        page = int(request.args.get("page", 1))
        ALL = db.session.query(DailyStatistics.id, DailyStatistics.processing_date)
        count = ALL.count()

        STATS = ALL.order_by(expression.desc(DailyStatistics.processing_date))\
            .offset((page - 1)*self.page_size).limit(self.page_size).cte("STATS")

        CALCULATIONS = db.session.query(STATS.c.id, GameStat.game_id, GameStat.currency,
                                        func.coalesce(func.sum(GameStat.award), 0),
                                        func.coalesce(func.sum(GameStat.bet), 0)).\
            outerjoin(GameStat, STATS.c.processing_date == func.date(GameStat.game_start)).\
            group_by(STATS.c.id, GameStat.game_id, GameStat.currency).subquery("CALCULATIONS")

        query_result = db.session.query(CALCULATIONS, DailyStatistics.processing_date,
                                        DailyStatistics.interactive_show, DailyStatistics.cheating_dice,
                                        DailyStatistics.qna).\
            join(DailyStatistics, CALCULATIONS.c.id == DailyStatistics.id).\
            order_by(expression.desc(DailyStatistics.processing_date)).all()

        table_list = []
        for row in query_result:
            if table_list and table_list[-1]["id"] == row[0]:
                item = table_list[-1]
            else:
                item = {
                    "id": row[0],
                    "date": row[5].strftime("%Y-%m-%d"),
                    "stream_total": row[6],
                    "uncompleted": time.mktime(row[5].timetuple()) < time.mktime(datetime(2016, 11, 1).timetuple()),
                    "dice_stat": {
                        "count": row[7],
                        "consumption": {
                            "vfc": 0,
                            "vcy": 0
                        },
                        "compensation": {
                            "vfc": 0,
                            "vcy": 0
                        }
                    },
                    "qna_stat": {
                        "count": row[8],
                        "consumption": {
                            "vfc": 0,
                            "vcy": 0
                        },
                        "compensation": {
                            "vfc": 0,
                            "vcy": 0
                        }
                    }
                }
                table_list.append(item)
            self.update_item(item, row[1], row[2], row[3], row[4])

        return table_list, count

    @expose("/")
    def index_view(self):
        data, count = self.get_list()
        num_pages = num_of_page(count, self.page_size)
        page = int(request.args.get("page", 1))

        def pager_url(p):
            return url_for(".index_view", page=p+1)

        kwargs = {
            "data": data,
            "num_pages": num_pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": self.page_size,
            "total": count
        }
        return self.render("statistics/interactive_game_stat.html", **kwargs)

    @expose('/detail/<id>')
    def detail_list(self, id):
        stat = DailyStatistics.query.get(id)
        page = int(request.args.get("page", 1))

        result = GameStat.query.filter(func.date(GameStat.game_start) == stat.processing_date).\
            join(AppUser, GameStat.compere_id == AppUser.uuid).\
            join(UserCertification, AppUser.uid == UserCertification.uid).\
            order_by(GameStat.game_start).\
            add_columns(UserCertification.nickname).paginate(page, self.page_size, False)

        data = []
        for item in result.items:
            duration = item.GameStat.game_end - item.GameStat.game_start
            duration -= timedelta(microseconds=duration.microseconds)

            data.append({
                "room_id": item.GameStat.room_id,
                "login_name": item.nickname,
                "currency": item.GameStat.currency,
                "start": item.GameStat.game_start.strftime("%H:%M:%S"),
                "end": item.GameStat.game_end.strftime("%H:%M:%S"),
                "duration": duration,
                "consumption": item.GameStat.bet,
                "compensation": item.GameStat.award + item.GameStat.bet,
                "game_id": item.GameStat.game_id
            })

        def pager_url(p):
            return url_for(".detail_list", page=p+1, id=id)

        kwargs = {
            "data": data,
            "num_pages": result.pages,
            "page": page - 1,
            "pager_url": pager_url,
            "page_size": self.page_size,
            "total": result.total,
            "title": u"{} 游戏记录".format(stat.processing_date.strftime("%Y-%m-%d"))
        }

        return self.render("statistics/interactive_game_list.html", **kwargs)


class CommonStatView(AuthenticatedModelView):
    column_list = ("processing_date", "user_registered", "uesr_logined", "total_user", "dau", "user_recharged",
                   "recharged_amount")
    column_default_sort = ("processing_date", True)
    column_searchable_list = ("processing_date",)
    column_sortable_list = ("processing_date", "user_registered", "uesr_logined", "total_user", "dau", "user_recharged",
                            "recharged_amount")
    column_labels = {
        "processing_date": u"日期",
        "user_registered": u"新注册用户",
        "uesr_logined": u"登录设备数",
        "total_user": u"总注册用户",
        "dau": u"日活跃用户",
        "user_recharged": u"充值人数",
        "recharged_amount": u"充值总额（单位：元）"
    }

    column_formatters = {
        "processing_date": lambda v, c, m, n: m.processing_date.strftime("%Y-%m-%d")
    }

    column_descriptions = {
        "uesr_logined": u"进行过登录操作的设备数"
    }

    list_template = "indexed_thumbnail_list.html"
