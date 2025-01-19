from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='json')
def json_filter(value):
    """Convert a Python object to JSON string"""
    return mark_safe(json.dumps(value))

@register.filter
def upper(value):
    if isinstance(value, dict):
        return {k: v.upper() if isinstance(v, str) else v for k, v in value.items()}
    return value.upper() if isinstance(value, str) else value
