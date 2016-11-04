# -*- coding: utf-8 -*-
import os
import hashlib
from flask import make_response, jsonify

from config import IMAGE_DIR, IMAGE_BASE_PATH


def is_file_exists(file_url):
    if not file_url:
        return False
    path = file_url.replace(IMAGE_BASE_PATH, "", 1).replace("/", os.sep)
    if path.startswith(os.sep):
        path = path[1:]
    return os.path.exists(os.path.join(IMAGE_DIR, path))


def hash_md5(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


def hash_sha1(s):
    m = hashlib.sha1()
    m.update(s)
    return m.hexdigest()


def json_response(data, code):
    return make_response(jsonify(data), code)
