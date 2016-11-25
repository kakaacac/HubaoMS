# -*- coding: utf-8 -*-
import psycopg2
import time
from datetime import datetime, timedelta
import apscheduler
import logging
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from utils.NetEase import NetEase
from utils.RedisPool.redis_pool import RedisPool
from views.user import AccountManagementView
from config import HOST, PORT, USER, PASSWORD, DATABASE, DB_URL, REDIS_SENTINELS, REDIS_SETTINGS, SOCKET_TIMEOUT, \
    SCHEDULER_FREQ


netease = NetEase()
redis = RedisPool(sentinels=REDIS_SENTINELS, socket_timeout=SOCKET_TIMEOUT, **REDIS_SETTINGS)

def send_broadcast(message, rooms):
    netease.send_to_chatrooms(rooms, 0, msg=message)


def unblock_account_job(uid):
    conn = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
    cur = conn.cursor()

    cur.execute("SELECT uuid, locked, locked_time, rid, room.enable, disable_time FROM users "
                "INNER JOIN room ON users.uid=room.uid WHERE users.uid=%s;", (uid,))
    uuid, locked, locked_time, rid, enable, disable_time = cur.fetchone()

    if locked:
        cur.execute("UPDATE users SET locked=FALSE WHERE uid=%s", (uid,))

        # Unblock room
        if not enable and locked_time == disable_time:
            cur.execute("UPDATE room SET enable=TRUE, control_flag=0 WHERE rid=%s", (rid,))
            AccountManagementView.control_video_stream(rid, uuid, action=1)
            redis.master().hdel("control:block:room", rid)

        conn.commit()
        redis.master().hdel("control:block:account", uuid.replace("-", ""))


def unblock_room_job(rid):
    conn = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
    cur = conn.cursor()

    cur.execute("SELECT uuid, enable FROM room INNER JOIN users ON room.uid=users.uid WHERE rid=%s;", (rid,))
    uuid, enable = cur.fetchone()

    if not enable:
        #restore video stream
        AccountManagementView.control_video_stream(rid, uuid, action=1)

        cur.execute("UPDATE room SET enable=TRUE, control_flag=0 WHERE rid=%s", (rid,))
        conn.commit()
        redis.master().hdel("control:block:room", rid)


class JobProcessor(object):
    def __init__(self):
        self.conn = None
        self.cur = None
        self.netease = netease

        # Start scheduler
        self.scheduler = BackgroundScheduler()
        self.db_jobstore = SQLAlchemyJobStore(url=DB_URL)
        self.scheduler.add_jobstore(self.db_jobstore, alias='db_jobstore')

        self.func_mapper = {
            "broadcast": self.start_broadcast,
            "unblock_account": self.process_unblock_acct,
            "unblock_room": self.process_unblock_room
        }

    def connect(self):
        self.conn = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
        self.cur = self.conn.cursor()

    def disconnect(self):
        self.cur.close()
        self.conn.close()

    @staticmethod
    def _normalize_job_start_time(start_time, time_format="%Y-%m-%d %H:%M:%S"):
        if isinstance(start_time, (str, unicode)):
            st = datetime.strptime(start_time, time_format)
        else:
            st = start_time

        # To ensure start time is greater than the current time. Might be improved.
        return max(st, datetime.now() + timedelta(seconds=2))

    def load_pending_jobs(self):
        self.cur.execute("SELECT sj.*, aj.id FROM scheduled_jobs sj left join apscheduler_jobs aj on sj.job_id=aj.id "
                         "WHERE status <= 1;")
        jobs = []
        for job in self.cur.fetchall():
            jobs.append({
                "job_id": job[0],
                "job_type": job[1],
                "status": job[2],
                "job_args": job[3],
                "job_function": job[4],
                "start_time": job[5],
                "end_time": job[6],
                "job_interval": job[7],
                "running": job[8] is not None
            })
        return jobs

    def process_job(self, job):
        func = self.func_mapper.get(job["job_function"])
        func(job)

    def start_broadcast(self, job):
        job_kwargs = {
            "kwargs": job["job_args"],
            "minutes": job["job_interval"],
            "start_date": self._normalize_job_start_time(job["start_time"]),
            "end_date": job["end_time"],
            "id": job["job_id"]
        }
        self.scheduler.add_job(send_broadcast, job["job_type"], jobstore='db_jobstore', **job_kwargs)

    def process_unblock_acct(self, job):
        job_kwargs = {
            "id": job["job_id"],
            "run_date": job["start_time"]
        }
        job_kwargs.update(job["job_args"])
        self.scheduler.add_job(unblock_account_job, job["job_type"], jobstore='db_jobstore', **job_kwargs)

    def process_unblock_room(self, job):
        job_kwargs = {
            "id": job["job_id"],
            "run_date": job["start_time"]
        }
        job_kwargs.update(job["job_args"])
        self.scheduler.add_job(unblock_room_job, job["job_type"], jobstore='db_jobstore', **job_kwargs)

    def run(self):
        self.scheduler.start()
        while 1:
            try:
                self.connect()
                for job in self.load_pending_jobs():
                    # Job to be executed
                    if job["status"] == 0:
                        if job["running"]:
                            try:
                                self.scheduler.remove_job(job_id=job["job_id"], jobstore='db_jobstore')
                            except apscheduler.jobstores.base.JobLookupError as e:
                                logging.error(e.message)
                        self.process_job(job)
                        self.cur.execute("UPDATE scheduled_jobs SET status=2 WHERE job_id=%s", (job["job_id"],))
                        self.conn.commit()

                    # Job to be terminated
                    else:
                        try:
                            self.scheduler.remove_job(job_id=job["job_id"], jobstore='db_jobstore')
                        except apscheduler.jobstores.base.JobLookupError as e:
                            logging.error(e.message)
                        self.cur.execute("UPDATE scheduled_jobs SET status=3 WHERE job_id=%s", (job["job_id"],))
                        self.conn.commit()

                self.disconnect()
                time.sleep(SCHEDULER_FREQ)

            except Exception as e:
                logging.error(e.message)


if __name__ == '__main__':
    processor = JobProcessor()
    processor.run()

