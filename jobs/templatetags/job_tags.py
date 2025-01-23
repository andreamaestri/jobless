import json as json_lib
from django import template
from django.utils.safestring import mark_safe
from ..utils.skill_icons import SKILL_ICONS, DARK_VARIANTS, ICON_NAME_MAPPING

register = template.Library()

@register.filter
def json(obj):
    """Convert a Python object to JSON string"""
    return mark_safe(json_lib.dumps(obj))

import logging

logger = logging.getLogger(__name__)

@register.filter
def get_skill_icon(skill):
    """Get the icon for a skill"""
    try:
        if hasattr(skill, 'get_icon'):
            icon = skill.get_icon()
            logger.debug(f"Got icon from skill object: {icon}")
            return icon
        
        # Handle string input
        if isinstance(skill, str):
            skill_name = skill.lower()
            # First check ICON_NAME_MAPPING
            if skill_name in ICON_NAME_MAPPING:
                icon = ICON_NAME_MAPPING[skill_name]
                logger.debug(f"Got icon from mapping for {skill_name}: {icon}")
                return icon
            # Then check SKILL_ICONS
            for icon, name in SKILL_ICONS:
                if name.lower() == skill_name:
                    logger.debug(f"Got icon from SKILL_ICONS for {skill_name}: {icon}")
                    return icon
        
        logger.warning(f"No icon found for skill: {skill}, using default")
        return 'heroicons:academic-cap'  # Default icon matching the format of other icons
    except Exception as e:
        logger.error(f"Error getting icon for skill {skill}: {str(e)}")
        return 'heroicons:academic-cap'

@register.filter
def status_badge(status):
    """Get the appropriate badge class for a status"""
    badges = {
        'interested': 'badge-info',
        'applied': 'badge-primary',
        'interviewing': 'badge-secondary',
        'rejected': 'badge-error',
        'accepted': 'badge-success',
    }
    return badges.get(status.lower(), 'badge-ghost')

@register.filter
def status_icon(status):
    """Get the appropriate icon for a status"""
    icons = {
        'interested': 'heroicons:star',
        'applied': 'heroicons:paper-airplane',
        'interviewing': 'heroicons:users',
        'rejected': 'heroicons:x-circle',
        'accepted': 'heroicons:check-circle',
    }
    return icons.get(status.lower(), 'heroicons:question-mark-circle')

@register.filter(name='skills_to_json')
def skills_to_json(skills):
    """Convert skills queryset to JSON"""
    return mark_safe(json_lib.dumps([{
        'name': str(skill),
        'icon': skill.get_icon() if hasattr(skill, 'get_icon') else 'heroicons:academic-cap',
        'icon_dark': skill.get_icon_dark() if hasattr(skill, 'get_icon_dark') else None
    } for skill in skills]))

@register.simple_tag
def get_all_skill_icons():
    """Get all available skill icons"""
    return SKILL_ICONS
