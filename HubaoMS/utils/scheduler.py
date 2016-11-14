# -*- coding: utf-8 -*-
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from multiprocessing import Process
import time
from datetime import datetime, timedelta

from utils import integrated_redis, job_queue
from config import DB_URL

def get_redis_jobstore(db=1, jobs_key="apscheduler:jobs", run_times_key="apscheduler:run_times"):
    jobstore = RedisJobStore(db=db, jobs_key=jobs_key, run_times_key=run_times_key)
    jobstore.redis = integrated_redis
    return jobstore


# class JobProcessor(object):
#     def __init__(self, sched, queue):
#         self.sched = sched
#         self.queue = queue
#
#     def process_job(self):
#         job = self.queue.get()
#         print job
#
#     def receive_job(self, freq=1):
#         while 1:
#             while not self.queue.empty():
#                 self.process_job()
#             time.sleep(freq)
#
#     def run(self):
#         self.ps = Process(target=self.receive_job)
#         self.ps.start()


def normalize_job_start_time(start_time, time_format="%Y-%m-%d %H:%M:%S"):
    if isinstance(start_time, (str, unicode)):
        st = datetime.strptime(start_time, time_format)
    else:
        st = start_time

    # To ensure start time is greater than the current time. Might be improved.
    return max(st, datetime.now() + timedelta(seconds=2))


def process_job(sched, queue):
    job = queue.get()
    action = job.get("action")

    if action == "add":
        if job["trigger"] == 'interval':
            st = job["job_kwargs"]["start_date"]
            job["job_kwargs"]["start_date"] = normalize_job_start_time(st)
        sched.add_job(job["func"], job["trigger"], jobstore='db_jobstore', **job["job_kwargs"])

    elif action == "stop":
        sched.remove_job(job_id=job["id"], jobstore='db_jobstore')
    else:
        raise Exception("Unknown job type")


# Instance method cannot be pickled, so pure method is used for multiprocessing.
def receive_job(queue, freq=1):
    scheduler = BackgroundScheduler()
    db_jobstore = SQLAlchemyJobStore(url=DB_URL)
    scheduler.add_jobstore(db_jobstore, alias='db_jobstore')
    scheduler.start()
    while 1:
        while not queue.empty():
            process_job(scheduler, queue)
        time.sleep(freq)


def init_scheduler():
    # processor = JobProcessor(scheduler, job_queue)
    # processor.run()
    ps = Process(target=receive_job, args=(job_queue,))
    ps.start()

