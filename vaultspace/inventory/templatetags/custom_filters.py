import json
from django import template

register = template.Library()

@register.filter
def loads(value):
    return json.loads(value)
