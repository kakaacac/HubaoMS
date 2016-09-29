# -*- coding: utf-8 -*-
from flask import Markup


def button(buttons, btn_class="btn btn-default"):
    """
    :param buttons: list of tuple in format (display value, post address)
    :return: html
    """
    btn_html = u"".join([u'<a href="{0}" class="{1}">{2}</a>'.format(btn[1], btn_class, btn[0]) for btn in buttons])
    return Markup(btn_html)


def colorize(text, color):
    return Markup(u'<span style="color: {0}">{1}</span>'.format(color, text))