# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from wtforms.validators import DataRequired, ValidationError

class BroadcastTarget(DataRequired):
    def __call__(self, form, field):
        if form.range.data != 'all':
            super(BroadcastTarget, self).__call__(form, field)


class Endtime(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if field.data < form.start_time.data or field.data + timedelta(seconds=30) < datetime.now():
            raise ValidationError("Invalid end time")


class AwardAmount(DataRequired):
    def __call__(self, form, field):
        if not form.random.data:
            super(AwardAmount, self).__call__(form, field)