# -*- coding: utf-8 -*-
import logging
from flask import Flask

from config import USER, PASSWORD, HOST, PORT, DATABASE, SOCKET_TIMEOUT, REDIS_SETTINGS, REDIS_SENTINELS
from models import db
from utils.login_manager import login_manager
from utils import redis, integrated_redis
from manage import admin, api
from utils.scheduler import init_scheduler

logging.basicConfig(level=logging.ERROR)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{un}:{pw}@{h}:{p}/{db}".format(
    un=USER, pw=PASSWORD, h=HOST, p=PORT, db=DATABASE
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SOCKET_TIMEOUT"] = SOCKET_TIMEOUT
app.config["REDIS_SENTINELS"] = REDIS_SENTINELS
app.config["REDIS_SETTINGS"] = REDIS_SETTINGS

app.secret_key = "test"

# Start a schedule to execute or eliminate uncompleted jobs
# init_scheduler()

db.init_app(app)
login_manager.init_app(app)
redis.init_app(app)
admin.init_app(app)
api.init_app(app)
integrated_redis.init_app(app)

if __name__ == '__main__':
    # Start a schedule to execute or eliminate uncompleted jobs
    init_scheduler()
    app.run(debug=True, use_reloader=False)
    # from apscheduler.schedulers.background import BackgroundScheduler
    # from datetime import datetime, timedelta
    # scheduler = BackgroundScheduler()
    # def hello():
    #     with open(r"E:\hubao\HubaoMS\test.txt" "a") as f:
    #         f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # scheduler.add_job(hello, 'interval', seconds=10)
    # scheduler.start()
