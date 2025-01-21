from django import template
import json
from django.utils.safestring import mark_safe
from jobs.utils.skill_icons import ICON_NAME_MAPPING, DARK_VARIANTS, SKILL_ICONS

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
        'name': str(skill),  # Convert skill object to string
        'icon': getattr(skill, 'icon', 'heroicons:academic-cap'),  # Default icon if none set
        'icon_dark': getattr(skill, 'icon_dark', None)  # Optional dark variant
    } for skill in skills]))

@register.filter
def get_skill_icon(skill_name, dark=False):
    """
    Get the appropriate icon name for a given skill
    Args:
        skill_name: The name of the skill
        dark: Boolean indicating if dark variant should be used
    Returns:
        str: Icon name with preference for dark variants when available
    """
    # First check specific mappings in ICON_NAME_MAPPING
    icon = ICON_NAME_MAPPING.get(skill_name)
    if icon:
        # Always use dark variant if available
        dark_icon = DARK_VARIANTS.get(icon)
        if dark_icon:
            return dark_icon
        return icon

    # Normalize skill name by removing spaces and converting to lowercase
    normalized_name = skill_name.replace(' ', '').lower()
    
    # Handle specific skill name variations
    if normalized_name == 'androidstudio':
        normalized_name = 'androidstudio'
    
    # For generic skill icons, construct the base icon name
    skill_icon = f'skill-icons:{normalized_name}'
    
    # Always use dark variant if available
    dark_icon = DARK_VARIANTS.get(skill_icon)
    if dark_icon:
        return dark_icon

    # Check if the base icon exists in SKILL_ICONS
    for icon_name, _ in SKILL_ICONS:
        if icon_name.lower() == skill_icon.lower():
            # Always use dark variant if available
            dark_variant = DARK_VARIANTS.get(icon_name)
            if dark_variant:
                return dark_variant
            return icon_name
    
    # Fallback to default dark icon
    return 'heroicons:academic-cap-dark'

@register.simple_tag
def get_all_skill_icons():
    """Get all available skill icons and their names"""
    return SKILL_ICONS
