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

@register.filter(name='skills_to_json')
def skills_to_json(skills):
    """Convert skills queryset to JSON for use in data attributes"""
    return mark_safe(json.dumps([{
        'name': skill.name,
        'icon': skill.icon,
        'icon_dark': skill.icon_dark
    } for skill in skills]))
