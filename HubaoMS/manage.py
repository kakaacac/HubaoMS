# -*- coding: utf-8 -*-
from flask_admin import Admin
from flask_restful import Api

from views.base import IndexView
from views.user import UserView, FeedbackView, TaskView, AccountManagementView
from views.auth import LoginView, LogoutView
from views.compere import CompereView, CompereVerificationView, Withdrawal, CompereConf
from views.room import RoomView
from views.content import BannerView, RoomTagsView
from views.common import ImageUpload
from views.message import BroadcastView
from views.statistics import LiveShowStatView, GiftStatView
from models import db, AppUser, Feedback, Compere, CompereVerification, WithdrawHistory, Room, Banner, \
    Broadcast, RoomTags, DailyStatistics
from config import BASE_URL

api = Api(prefix=BASE_URL)
admin = Admin(name="Hubao TV", template_mode="bootstrap3", index_view=IndexView(name=u"首页", url=BASE_URL))

# Common
api.add_resource(ImageUpload, "/image_upload", endpoint="image_upload")

# User
admin.add_view(UserView(name=u"用户列表", category=u'用户', endpoint='user', session=db.session, model=AppUser,
                        menu_icon_type='glyph', menu_icon_value='glyphicon-user'))
admin.add_view(FeedbackView(name=u"用户反馈", endpoint='feedback', category=u'用户', session=db.session, model=Feedback,
                            menu_icon_type='glyph', menu_icon_value='glyphicon-comment'))
admin.add_view(TaskView(name=u"任务列表", category=u'用户', endpoint='task',
                        menu_icon_type='glyph', menu_icon_value='glyphicon-tasks'))
admin.add_view(AccountManagementView(name=u"账号封停", category=u'用户', endpoint="account", session=db.session,
                                     model=AppUser, menu_icon_type='glyph', menu_icon_value='glyphicon-lock'))

# Compere
admin.add_view(CompereView(name=u"主播列表", category=u"主播", endpoint="compere", session=db.session, model=Compere,
                        menu_icon_type='glyph', menu_icon_value='glyphicon-user'))
admin.add_view(CompereVerificationView(name=u"主播认证", category=u"主播", endpoint="verification",
                                       session=db.session, model=CompereVerification,
                                       menu_icon_type='glyph', menu_icon_value='glyphicon-check'))
admin.add_view(Withdrawal(name=u"提现记录", category=u"主播", endpoint="withdrawal", session=db.session,
                          model=WithdrawHistory, menu_icon_type='glyph', menu_icon_value='glyphicon-credit-card'))
admin.add_view(CompereConf(name=u"主播配置", category=u"主播", endpoint='configuration',
                           menu_icon_type='glyph', menu_icon_value='glyphicon-wrench'))

# Room
admin.add_view(RoomView(name=u"房间列表", category=u"直播间", endpoint="room", session=db.session, model=Room,
                        menu_icon_type='glyph', menu_icon_value='glyphicon-facetime-video'))

# Content
admin.add_view(BannerView(name=u"轮播图列表", category=u"内容管理", endpoint="banner", session=db.session, model=Banner,
                          menu_icon_type='glyph', menu_icon_value='glyphicon-picture'))
admin.add_view(RoomTagsView(name=u"房间标签", category=u"内容管理", endpoint="tags", session=db.session, model=RoomTags,
                            menu_icon_type='glyph', menu_icon_value='glyphicon-tags'))

# Message
admin.add_view(BroadcastView(name=u"广播列表", category=u"消息发布", endpoint="broadcast", session=db.session,
                             model=Broadcast, menu_icon_type='glyph', menu_icon_value='glyphicon-bullhorn'))

# Statistics
admin.add_view(LiveShowStatView(name=u"直播统计", category=u"统计数据", endpoint="show_statistics",
                                session=db.session, model=DailyStatistics,
                                menu_icon_type='glyph', menu_icon_value='glyphicon-film'))
admin.add_view(GiftStatView(name=u"礼物统计", category=u"统计数据", endpoint="gift_statistics",
                            session=db.session, model=DailyStatistics,
                            menu_icon_type='glyph', menu_icon_value='glyphicon-gift'))

# Auth
admin.add_view(LoginView(name=u"登录", category=u"管理", endpoint='login',
                         menu_icon_type='glyph', menu_icon_value='glyphicon-log-in'))
admin.add_view(LogoutView(name=u"登出", category=u"管理", endpoint='logout',
                          menu_icon_type='glyph', menu_icon_value='glyphicon-log-out'))