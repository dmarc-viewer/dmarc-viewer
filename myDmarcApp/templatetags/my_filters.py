from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escapejs
import json

register = template.Library()

@register.filter
def to_json(obj):
    """
    Dump python object as json string, remove whitespaces, escapejs and parse on client as json
    """
    # separators is passed to remove whitespace in output
    return  mark_safe('JSON.parse("%s")' % escapejs(json.dumps(obj, separators=(',', ':'))))

