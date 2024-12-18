from django.urls import reverse

def navigation(request):
    navigation_items = [
        {'url': 'home:home', 'icon': 'octicon:home-24', 'label': 'Dashboard'},
        {'url': 'jobs:list', 'icon': 'octicon:briefcase-24', 'label': 'Jobs'},
        {'url': 'events:list', 'icon': 'octicon:calendar-24', 'label': 'Events'},
        {'url': 'contacts:list', 'icon': 'octicon:people-24', 'label': 'Contacts'},
        {'url': 'ai_assistant:assistant', 'icon': 'octicon:copilot-24', 'label': 'AI Assistant'},
    ]
    
    # Convert URL names to actual URLs
    for item in navigation_items:
        item['url'] = request.build_absolute_uri(reverse(item['url']))
    
    return {'navigation_items': navigation_items}
