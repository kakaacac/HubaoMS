# -*- coding: utf-8 -*-
import json
import random
import string
import time
import uuid
from urllib import urlencode
import requests

from config import NETEASE_APP_KEY, NETEASE_APP_SECRET, NETEASE_BASE_URL, NETEASE_TIMEOUT
from utils.functions import hash_sha1

class NetEase(object):
    def __init__(self, app_key=NETEASE_APP_KEY, app_secret = NETEASE_APP_SECRET):
        self.app_key = app_key
        self.app_secret = app_secret

    @staticmethod
    def _generate_random_number(length=32):
        return "".join([random.choice(string.ascii_lowercase + string.digits) for _ in range(length)])

    @staticmethod
    def _get_current_time():
        return str(int(time.time()))

    def generate_checksum(self):
        return hash_sha1(self.app_secret + self.nonce + self.timestamp)

    def generate_header(self):
        self.nonce = self._generate_random_number()
        self.timestamp = self._get_current_time()

        checksum = self.generate_checksum()

        return {
            'AppKey': NETEASE_APP_KEY,
            'CheckSum': checksum,
            'Nonce': self.nonce,
            'CurTime': self.timestamp,
            'Content-Type': "application/x-www-form-urlencoded"
        }

    def send_to_chatroom(self, room_id, msg_type, msg=None, ext=None):
        url = NETEASE_BASE_URL + '/chatroom/sendMsg.action'
        payload = {
            'roomid': room_id,
            'msgId': str(uuid.uuid4()),
            'fromAccid': 'system',
            'msgType': msg_type
        }
        if msg:
            payload['attach'] = msg.encode("utf-8")
        if ext:
            payload['ext'] = json.dumps(ext)

        return requests.post(url=url, data=urlencode(payload), headers=self.generate_header(), timeout=NETEASE_TIMEOUT)

    def send_to_chatrooms(self, rooms, msg_type, msg=None, ext=None):
        for room_id in rooms:
            self.send_to_chatroom(room_id, msg_type, msg, ext)


if __name__ == '__main__':
    # import sys
    # sys.path.append("")
    # print sys.path
    # import random
    import logging
    logging.getLogger('requests').setLevel(level=logging.ERROR)
    from config import HOST, PORT, USER, PASSWORD, DATABASE
    import psycopg2
    net = NetEase()

    conn = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
    # conn = psycopg2.connect(host="10.116.108.164", port=5432, user="postgres", password="L4K3J4Y72yLy", database="hubao_tv_db")
    cur = conn.cursor()
    # cur.execute("select username from chat_account c left join users u on c.id=replace(u.uuid::\"varchar\", '-', '') where uuid is null")
    # print len(cur.fetchall())

    # for username in cur.fetchall():
    #     r = requests.post("https://api.netease.im/nimserver/user/updateUinfo.action", data=urlencode({"accid":username[0], "name":u"游客{}".format(random.randint(100000, 999999)).encode("utf-8")}), headers=net.generate_header())
    #     if r.status_code != 200:
    #         print r.content
    # net = NetEase()
    # print requests.post("https://api.netease.im/nimserver/user/updateUinfo.action", data=urlencode({"accid":"system", "name":u"系统广播".encode("utf-8")}), headers=net.generate_header()).content
    print requests.post("https://api.netease.im/nimserver/user/getUinfos.action", data=urlencode({"accids":["bc059eb84ff6fa2b43430143aa8ffebe"]}), headers=net.generate_header()).content

    # cur.execute("select username, avatar from users u inner join chat_account c on c.id=replace(u.uuid::\"varchar\", '-', '') where avatar != ''")
    # fail = 0
    # success = 0
    # for i, row in enumerate(cur.fetchall()):
    #     r = requests.post("https://api.netease.im/nimserver/user/updateUinfo.action", data=urlencode({"accid":row[0], "icon":row[1]}), headers=net.generate_header())
    #     if r.status_code != 200:
    #         fail += 1
    #         print "{} -- Updating user {} failed. Count: {}".format(i + 1, row[0], fail)
    #     else:
    #         success += 1
    #         print "{} -- Successfully updated user {}. Count: {}".format(i + 1, row[0], success)
    #
    # print "Done. Success: {}. Failed: {}".format(success, fail)
    pass

