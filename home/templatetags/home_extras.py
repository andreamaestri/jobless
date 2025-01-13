from django import template

register = template.Library()

@register.filter
def percentage_of(value, total):
    """Calculate percentage of value against total"""
    try:
        return round((float(value) / float(total)) * 100) if total > 0 else 0
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
