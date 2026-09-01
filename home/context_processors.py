from django.urls import reverse
from django.utils.translation import gettext_lazy as _

def navigation(request):
    navigation_items = [
        {'url': 'home:home', 'icon': 'octicon:home-24', 'label': _('Overview')},
        {'url': 'jobs:list', 'icon': 'octicon:briefcase-24', 'label': _('Jobs')},
        {'url': 'jobs:nachweis', 'icon': 'octicon:checklist-24', 'label': _('Proof of efforts')},
        {'url': 'events:list', 'icon': 'octicon:calendar-24', 'label': _('Events')},
        {'url': 'contacts:list', 'icon': 'octicon:people-24', 'label': _('Contacts')},
        {'url': 'ai_assistant:assistant', 'icon': 'octicon:copilot-24', 'label': _('AI Assistant')},
    ]
    
    # Convert URL names to actual URLs
    for item in navigation_items:
        item['url'] = request.build_absolute_uri(reverse(item['url']))
    
    return {'navigation_items': navigation_items}
