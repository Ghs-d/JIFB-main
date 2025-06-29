# news/templatetags/news_filters.py

from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
    Splits the string `value` by `key`.
    Usage: {{ my_string|split:"," }}
    """
    return value.split(key)

@register.filter(name='strip')
def strip(value):
    """
    Removes leading/trailing whitespace from a string.
    Usage: {{ my_string|strip }}
    """
    return value.strip()
