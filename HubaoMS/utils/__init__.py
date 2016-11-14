# -*- coding: utf-8 -*-
import logging
import sys
from multiprocessing import Queue

from RedisPool.redis_pool import RedisPool
from RedisPool.IntegratedRedis import IntegratedRedis
from NetEase import NetEase

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

job_queue = Queue()

redis = RedisPool()
integrated_redis = IntegratedRedis()
netease = NetEase()