# -*- coding: utf-8 -*-
from multiprocessing import Queue

from RedisPool.redis_pool import RedisPool
from RedisPool.IntegratedRedis import IntegratedRedis
from NetEase import NetEase


job_queue = Queue()

redis = RedisPool()
integrated_redis = IntegratedRedis()
netease = NetEase()