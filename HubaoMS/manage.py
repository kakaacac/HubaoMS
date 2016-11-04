# -*- coding: utf-8 -*-
from flask_admin import Admin
from flask_restful import Api

from views.user import UserView, FeedbackView, TaskView, AccountManagementView
from views.auth import AuthView
from views.compere import CompereView, CompereVerificationView, Withdrawal, CompereConf
from views.room import RoomView
from views.content import BannerView, RoomTagsView
from views.common import ImageUpload
from views.message import BroadcastView
from views.statistics import LiveShowStatView, GiftStatView
from models import db, AppUser, Feedback, Compere, CompereVerification, WithdrawHistory, Room, Banner, \
    Broadcast, RoomTags, DailyStatistics
from config import BASE_URL, STATIC_BASE_URL

api = Api(prefix=BASE_URL)
admin = Admin(name="Hubao TV", template_mode="bootstrap3", url=BASE_URL)

# Common
api.add_resource(ImageUpload, "/image_upload", endpoint="image_upload")

# Auth
admin.add_view(AuthView(name="Login", endpoint='auth'))

# User
admin.add_view(UserView(name="User", category='User', endpoint='user', session=db.session, model=AppUser,
                        menu_icon_type='glyph', menu_icon_value='glyphicon-user'))
admin.add_view(FeedbackView(name="Feedback", endpoint='feedback', category='User', session=db.session, model=Feedback,
                            menu_icon_type='glyph', menu_icon_value='glyphicon-comment'))
admin.add_view(TaskView(name="Task", category='User', endpoint='task',
                        menu_icon_type='glyph', menu_icon_value='glyphicon-tasks'))
admin.add_view(AccountManagementView(name="Account", category="User", endpoint="account", session=db.session,
                                     model=AppUser, menu_icon_type='glyph', menu_icon_value='glyphicon-lock'))

# Compere
admin.add_view(CompereView(name="Compere", category="Compere", endpoint="compere", session=db.session, model=Compere,
                        menu_icon_type='glyph', menu_icon_value='glyphicon-user'))
admin.add_view(CompereVerificationView(name="Verification", category="Compere", endpoint="verification",
                                       session=db.session, model=CompereVerification,
                                       menu_icon_type='glyph', menu_icon_value='glyphicon-check'))
admin.add_view(Withdrawal(name="Withdrawal", category="Compere", endpoint="withdrawal", session=db.session,
                          model=WithdrawHistory, menu_icon_type='glyph', menu_icon_value='glyphicon-credit-card'))
admin.add_view(CompereConf(name="Configuration", category='Compere', endpoint='configuration',
                           menu_icon_type='glyph', menu_icon_value='glyphicon-wrench'))

# Room
admin.add_view(RoomView(name="Room", category="Room", endpoint="room", session=db.session, model=Room,
                        menu_icon_type='glyph', menu_icon_value='glyphicon-facetime-video'))

# Content
admin.add_view(BannerView(name="Banner", category="Content", endpoint="banner", session=db.session, model=Banner,
                          menu_icon_type='glyph', menu_icon_value='glyphicon-picture'))
admin.add_view(RoomTagsView(name="Room Tags", category="Content", endpoint="tags", session=db.session, model=RoomTags,
                            menu_icon_type='glyph', menu_icon_value='glyphicon-tags'))

# Message
admin.add_view(BroadcastView(name="Broadcast", category="Message", endpoint="broadcast", session=db.session,
                             model=Broadcast, menu_icon_type='glyph', menu_icon_value='glyphicon-bullhorn'))

# Statistics
admin.add_view(LiveShowStatView(name="ShowStatistics", category="Statistics", endpoint="show_statistics",
                                session=db.session, model=DailyStatistics,
                                menu_icon_type='glyph', menu_icon_value='glyphicon-film'))
admin.add_view(GiftStatView(name="GiftStatistics", category="Statistics", endpoint="gift_statistics",
                            session=db.session, model=DailyStatistics,
                            menu_icon_type='glyph', menu_icon_value='glyphicon-gift'))