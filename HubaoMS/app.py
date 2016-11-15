# -*- coding: utf-8 -*-
import logging
import platform
import os
from datetime import timedelta
from flask import Flask, send_from_directory

from config import USER, PASSWORD, HOST, PORT, DATABASE, SOCKET_TIMEOUT, REDIS_SETTINGS, REDIS_SENTINELS, \
    STATIC_BASE_URL, DEBUG, REMEMBER_DURATION, URL_SCHEME
from models import db
from utils.login_manager import login_manager
from utils import redis, integrated_redis
from manage import admin, api
from utils.scheduler import init_scheduler

logging.basicConfig(level=logging.ERROR)

app = Flask(__name__, static_url_path=STATIC_BASE_URL)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{un}:{pw}@{h}:{p}/{db}".format(
    un=USER, pw=PASSWORD, h=HOST, p=PORT, db=DATABASE
)
app.config["PREFERRED_URL_SCHEME"] = URL_SCHEME
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SOCKET_TIMEOUT"] = SOCKET_TIMEOUT
app.config["REDIS_SENTINELS"] = REDIS_SENTINELS
app.config["REDIS_SETTINGS"] = REDIS_SETTINGS
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=REMEMBER_DURATION)

app.secret_key = "test"

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('error/404.html', admin_base_template=admin.base_template), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Start a schedule to execute or eliminate uncompleted jobs
# init_scheduler()

db.init_app(app)
login_manager.init_app(app)
redis.init_app(app)
admin.init_app(app)
api.init_app(app)
integrated_redis.init_app(app)

if platform.system().lower() != 'windows':
    init_scheduler()

if __name__ == '__main__':
    # Start a schedule to execute or eliminate uncompleted jobs
    if platform.system().lower() == 'windows':
        init_scheduler()
    app.run(debug=DEBUG, use_reloader=False)
