# -*- coding: utf-8 -*-
import hashlib
import os
from PIL import Image
from flask import make_response
from flask_login import login_required
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from config import IMAGE_DIR, IMAGE_BASE_PATH


class ImageUpload(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("img", location="files", type=FileStorage)
        self.allowed_extensions = ('gif', 'jpg', 'jpeg', 'png', 'tiff')
        super(ImageUpload, self).__init__()

    def is_file_allowed(self, filename):
        if not self.allowed_extensions:
            return True

        return ('.' in filename and
                filename.rsplit('.', 1)[1].lower() in
                map(lambda x: x.lower(), self.allowed_extensions))

    @login_required
    def post(self):
        args = self.reqparse.parse_args()
        img = args.get("img")
        if img is not None:
            if self.is_file_allowed(img.filename):
                try:
                    image = Image.open(img)
                except Exception:
                    return make_response(u"错误文件格式", 400)

                img_format = image.format.lower()
                if img_format in self.allowed_extensions:
                    imgbyte = image.tobytes()

                    md5 = hashlib.md5()
                    md5.update(imgbyte)
                    hash_str = md5.hexdigest()

                    path = os.path.join(IMAGE_DIR, hash_str[:4], hash_str[4:8])
                    img_path = os.path.join(path, hash_str[8:] + '.' + img_format)
                    if not os.path.exists(path):
                        os.makedirs(path)

                    image.save(img_path)
                else:
                    return make_response(u"文件格式错误", 400)
            else:
                return make_response(u"文件格式错误", 400)
        else:
            return make_response(u"文件不能为空", 400)

        return {
                   "img_url": "/".join([IMAGE_BASE_PATH, hash_str[:4], hash_str[4:8], hash_str[8:] + '.' + img_format])
               }, 200