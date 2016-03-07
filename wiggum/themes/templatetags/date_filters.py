import datetime

from django import template

register = template.Library()


@register.filter(name='epoch_datetime')
def epochToDatetime(value):
    return datetime.datetime.fromtimestamp(int(value))
