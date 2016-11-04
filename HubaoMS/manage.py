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
from config import BASE_URL

api = Api()
admin = Admin(name="Hubao TV", template_mode="bootstrap3", url=BASE_URL)

# Common
api.add_resource(ImageUpload, "/image_upload", endpoint="image_upload")

# Auth
admin.add_view(AuthView(name="Login", url='/auth'))

# User
admin.add_view(UserView(name="User", category='User', endpoint='user', session=db.session, model=AppUser))
admin.add_view(FeedbackView(name="Feedback", endpoint='feedback', category='User', session=db.session, model=Feedback))
admin.add_view(TaskView(name="Task", category='User', endpoint='task'))
admin.add_view(AccountManagementView(name="Account", category="User", endpoint="account", session=db.session, model=AppUser))

# Compere
admin.add_view(CompereView(name="Compere", category="Compere", endpoint="compere", session=db.session, model=Compere))
admin.add_view(CompereVerificationView(name="Verification", category="Compere", endpoint="verification", session=db.session, model=CompereVerification))
admin.add_view(Withdrawal(name="Withdrawal", category="Compere", endpoint="withdrawal", session=db.session, model=WithdrawHistory))
admin.add_view(CompereConf(name="Configuration", category='Compere', endpoint='configuration'))

# Room
admin.add_view(RoomView(name="Room", category="Room", endpoint="room", session=db.session, model=Room))

# Content
admin.add_view(BannerView(name="Banner", category="Content", endpoint="banner", session=db.session, model=Banner))
admin.add_view(RoomTagsView(name="Room Tags", category="Content", endpoint="tags", session=db.session, model=RoomTags))

# Message
admin.add_view(BroadcastView(name="Broadcast", category="Message", endpoint="broadcast", session=db.session, model=Broadcast))

# Statistics
admin.add_view(LiveShowStatView(name="ShowStatistics", category="Statistics", endpoint="show_statistics", session=db.session, model=DailyStatistics))
admin.add_view(GiftStatView(name="GiftStatistics", category="Statistics", endpoint="gift_statistics", session=db.session, model=DailyStatistics))