# -*- coding: utf-8 -*-
# __author__ = 'billy'
from redis.sentinel import Sentinel

from flask import current_app as app
from redis_master import RedisMaster
from redis_slave import RedisSlave


class RedisPool(object):
    def __init__(self, sentinels=None, master_name=None, password=None, db=None,
                 socket_timeout=None, app=None):

        self.sentinels = sentinels
        self.master_name = master_name
        self.password = password
        self.db = db
        self.socket_timeout = socket_timeout

        self.sentinel = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        if not self.socket_timeout:
            self.socket_timeout = app.config['SOCKET_TIMEOUT']

        if self.sentinels is None and 'REDIS_SENTINELS' not in app.config:
            raise ValueError('sentinels')
        if self.master_name is None and (
                    'REDIS_SETTINGS' not in app.config or 'master_name' not in app.config['REDIS_SETTINGS']):
            raise ValueError('master_name')

        sentinels = app.config['REDIS_SENTINELS']
        self.master_name = app.config['REDIS_SETTINGS']['master_name']

        if 'REDIS_SETTINGS' in app.config:
            if self.password is None and 'password' in app.config['REDIS_SETTINGS']:
                self.password = app.config['REDIS_SETTINGS']['password']
            if self.db is None and 'db' in app.config['REDIS_SETTINGS']:
                self.db = app.config['REDIS_SETTINGS']['db']

        self.sentinel = Sentinel(sentinels, password=self.password, db=self.db, socket_timeout=self.socket_timeout)

    def master(self):
        return RedisMaster(self.sentinel, self.master_name, self.socket_timeout)

    def slave(self):
        return RedisSlave(self.sentinel, self.master_name, self.socket_timeout)

    # PUB/SUB
    def pubsub(self, **kwargs):
        master = self.slave()
        if master is None:
            return None
        else:
            return master.__get_redis__().pubsub(**kwargs)

    def publish(self, channel, message):
        slave = self.slave()
        if slave is None:
            return None
        else:
            return slave.__get_redis__().publish(channel, message)