# -*- coding: utf-8 -*-
import logging
import os
from datetime import timedelta
from flask import Flask, send_from_directory

from config import USER, PASSWORD, HOST, PORT, DATABASE, SOCKET_TIMEOUT, REDIS_SETTINGS, REDIS_SENTINELS, \
    STATIC_BASE_URL, DEBUG, REMEMBER_DURATION, URL_SCHEME
from models import db
from utils.login_manager import login_manager
from utils import redis, integrated_redis
from manage import admin, api

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.ERROR)

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

# @app.before_request
# def before_request():
#     if URL_SCHEME == "https":
#         if request.url.startswith('http://'):
#             url = request.url.replace('http://', 'https://', 1)
#             return redirect(url, code=301)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

db.init_app(app)
login_manager.init_app(app)
redis.init_app(app)
admin.init_app(app)
api.init_app(app)
integrated_redis.init_app(app)

if __name__ == '__main__':
    app.run(debug=DEBUG, use_reloader=False)
