# -*- coding: utf-8 -*-
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from utils.RedisPool import integrated_redis
from config import DB_URL

def get_redis_jobstore(db=1, jobs_key="apscheduler:jobs", run_times_key="apscheduler:run_times"):
    jobstore = RedisJobStore(db=db, jobs_key=jobs_key, run_times_key=run_times_key)
    jobstore.redis = integrated_redis

    return jobstore

redis_jobstore = get_redis_jobstore()
db_jobstore = SQLAlchemyJobStore(DB_URL)

def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(db_jobstore)
    scheduler.start()
