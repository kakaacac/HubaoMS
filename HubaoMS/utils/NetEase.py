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
    net = NetEase()
    print requests.post("https://api.netease.im/nimserver/user/updateUinfo.action", data=urlencode({"accid":"system", "name":u"系统广播".encode("utf-8")}), headers=net.generate_header()).content
    print requests.post("https://api.netease.im/nimserver/user/getUinfos.action", data=urlencode({"accids":["system"]}), headers=net.generate_header()).content
    pass

