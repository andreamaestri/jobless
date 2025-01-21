import json as json_lib  # Rename import to avoid naming conflict
from django import template
from django.utils.safestring import mark_safe
from jobs.utils.skill_icons import ICON_NAME_MAPPING, DARK_VARIANTS, SKILL_ICONS

register = template.Library()

@register.filter(name='json')
def json_filter(obj):
    """Convert a Python object to JSON string"""
    return mark_safe(json_lib.dumps(obj))  # Use renamed import

@register.filter
def upper(value):
    if isinstance(value, dict):
        return {k: v.upper() if isinstance(v, str) else v for k, v in value.items()}
    return value.upper() if isinstance(value, str) else value

@register.filter(name='skills_to_json')
def skills_to_json(skills):
    """Convert skills queryset to JSON for use in data attributes"""
    return mark_safe(json_lib.dumps([{
        'name': str(skill),  # Convert skill object to string
        'icon': getattr(skill, 'icon', 'heroicons:academic-cap'),  # Default icon if none set
        'icon_dark': getattr(skill, 'icon_dark', None)  # Optional dark variant
    } for skill in skills]))

@register.filter
def get_skill_icon(skill_name, dark=False):
    """
    Get the appropriate icon name for a given skill using the SKILL_ICONS mapping
    """
    # Handle case where skill_name is an object
    if hasattr(skill_name, 'name'):
        skill_name = skill_name.name
    elif hasattr(skill_name, '__str__'):
        skill_name = str(skill_name)

    if not isinstance(skill_name, str):
        return 'heroicons:academic-cap-dark'

    # Clean the skill name
    clean_name = skill_name.strip().lower().replace(' ', '').replace('(none)', '')
    
    # Try to find the icon in our SKILL_ICONS mapping first
    if clean_name in SKILL_ICONS:
        return SKILL_ICONS[clean_name]

    # Try different icon set prefixes
    prefixes = ['skill-icons:', 'logos:', 'devicon:']
    for prefix in prefixes:
        icon = f'{prefix}{clean_name}'
        if icon in ICON_NAME_MAPPING or icon in DARK_VARIANTS:
            return f'{icon}-dark' if prefix == 'skill-icons:' else icon

    return 'heroicons:academic-cap-dark'

@register.simple_tag
def get_all_skill_icons():
    """Get all available skill icons and their names"""
    return SKILL_ICONS

@register.filter
def status_badge(status):
    badges = {
        'APPLIED': 'badge-primary',
        'INTERVIEWING': 'badge-secondary',
        'OFFER': 'badge-success',
        'REJECTED': 'badge-error',
        'WITHDRAWN': 'badge-warning',
    }
    return badges.get(status, 'badge-ghost')

@register.filter
def status_icon(status):
    icons = {
        'APPLIED': 'octicon:paper-airplane-16',
        'INTERVIEWING': 'octicon:people-16',
        'OFFER': 'octicon:check-circle-16',
        'REJECTED': 'octicon:x-circle-16',
        'WITHDRAWN': 'octicon:skip-16',
    }
    return icons.get(status, 'octicon:dash-16')

@register.filter
def json(obj):
    return json_lib.dumps(obj)
