import json
from django import template

register = template.Library()

@register.filter(name='tojson', is_safe=True)
def tojson(value):
    """
    Safely convert a Python object to a JSON string.
    Usage: {{ value|tojson }}
    """
    return json.dumps(value)