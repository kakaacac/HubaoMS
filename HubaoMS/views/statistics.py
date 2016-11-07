# -*- coding: utf-8 -*-
from math import ceil
from datetime import timedelta, datetime
import time
from collections import OrderedDict, defaultdict
from flask import request, url_for
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView, tools
from flask_login import current_user
from sqlalchemy.sql import func, and_, or_, expression

from models import LiveStreamHistory, DailyStatistics, GameStat, GiftGiving, AppUser, UserCertification, Refund, db, \
    Room
from config import ROBOT_DEVICE_BEGIN, ROBOT_DEVICE_END
from utils.formatter import format_live_stat_actions, format_gift_stat_detail


class LiveShowStatView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

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
        4: "normal_show + paid_show"
    }

    def is_accessible(self):
        return current_user.is_authenticated

    def _get_sorting_column_by_idx(self, idx):
        if idx in self.extra_sorting:
            return self.extra_sorting[idx]
        else:
            return super(LiveShowStatView, self)._get_column_by_idx(idx)

    def _apply_sorting(self, query, joins, sort_column, sort_desc):
        if sort_column is not None:
            if sort_column in self._sortable_columns:
                sort_field = self._sortable_columns[sort_column]
                sort_joins = self._sortable_joins.get(sort_column)

                query, joins = self._order_by(query, joins, sort_joins, sort_field, sort_desc)
            else:
                if "+" in sort_column:
                    sum_columns = [tools.get_field_with_path(self.model, item.strip())[0] for item in sort_column.split('+')]
                    sum_column = sum_columns[0]
                    for c in sum_columns[1:]:
                        sum_column += c

                    if sort_desc:
                        query = query.order_by(expression.desc(sum_column))
                    else:
                        query = query.order_by(sum_column)

        else:
            order = self._get_default_order()

            if order:
                sort_field, sort_joins, sort_desc = order

                query, joins = self._order_by(query, joins, sort_joins, sort_field, sort_desc)

        return query, joins

    def is_sortable(self, name):
        extra_sort = [self._get_column_by_idx(i)[0] for i in self.extra_sorting.keys()]
        return True if name in extra_sort else super(LiveShowStatView, self).is_sortable(name)

    # Overriding view function for sorting column not in DB table
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
        sort_column = self._get_sorting_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0] if isinstance(sort_column, tuple) else sort_column

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

        return self.render(
            self.list_template,
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
            outerjoin(AppUser,
                 and_(GiftGiving.uid == AppUser.uid,
                      or_(AppUser.active_device < ROBOT_DEVICE_BEGIN,    # eliminate gifts given by robots
                          AppUser.active_device > ROBOT_DEVICE_END))).\
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
            "end_time": item[3].strftime("%Y-%m-%d %H:%M:%S"),
            "max_audience": item[4] or 0,
            "total_audience": item[5] or 0,
            "type": item[6],
            "duration": str(item[7] - timedelta(microseconds=item[7].microseconds)) if item[7] > zero_duration else str(zero_duration),
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
            "total": shows.total
        }

        return self.render("statistics/live_show_list.html", **kwargs)

    @expose('/detail/<id>')
    def stream_detail(self, id):
        room_id = int(id[:5])
        ts = int(id[5:15])
        microsec = int(id[15:])
        start_time = datetime.fromtimestamp(ts)
        start_time = start_time.replace(microsecond=microsec)

        stream = LiveStreamHistory.query.filter_by(rid=room_id, start_time=start_time).first_or_404()
        interactives = GameStat.query.filter(GameStat.room_id == room_id,
                                             GameStat.game_start >= start_time,
                                             GameStat.game_end <= stream.close_time).all()

        return id


class GiftStatView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_display_actions = False

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

    def is_accessible(self):
        return current_user.is_authenticated

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

        # Calculate number of pages
        if count > 0 and self.page_size:
            num_pages = int(ceil(count / float(self.page_size)))
        elif not self.page_size:
            num_pages = 0  # hide pager for unlimited page_size
        else:
            num_pages = None  # use simple pager

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

        # Calculate number of pages
        if count > 0 and self.page_size:
            num_pages = int(ceil(count / float(self.page_size)))
        elif not self.page_size:
            num_pages = 0  # hide pager for unlimited page_size
        else:
            num_pages = None  # use simple pager

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
            return url_for(".presenter_detail", page=p+1, sid=sid, uid=uid)

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

