# -*- coding: utf-8 -*-
from flask import Markup


def button(buttons, btn_class="btn btn-default", vertical=False):
    """
    :param buttons: list of tuple in format (display value, post address)
    :return: html
    """
    btn_html = []
    for btn in buttons:
        if len(btn) == 3:
            btn_html.append(u'<a href="{0}" class="{1}">{2}</a>'.format(btn[1], btn_class + ' ' + btn[2], btn[0]))
        else:
            btn_html.append(u'<a href="{0}" class="{1}">{2}</a>'.format(btn[1], btn_class, btn[0]))

    html = u'<br>'.join(btn_html) if vertical else u''.join(btn_html)
    return Markup(html)


def colorize(text, color):
    return Markup(u'<span style="color: {0}">{1}</span>'.format(color, text))