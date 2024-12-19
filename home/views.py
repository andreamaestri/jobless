from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from jobs.models import JobPosting
from events.models import Event
from contacts.models import Contact

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get search query from GET parameters
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        
        # Base querysets filtered by user
        jobs = JobPosting.objects.filter(user=self.request.user)
        events = Event.objects.filter(user=self.request.user)
        contacts = Contact.objects.filter(user=self.request.user)
        
        # Apply search if query exists
        if search_query:
            jobs = jobs.filter(
                Q(title__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            events = events.filter(
                Q(title__icontains=search_query) |
                Q(location__icontains=search_query)
            )
            contacts = contacts.filter(
                Q(name__icontains=search_query) |
                Q(company__icontains=search_query)
            )
            
        # Apply status filter for jobs if specified
        if status_filter:
            jobs = jobs.filter(status=status_filter)
            
        # Add to context with ordering
        context['recent_jobs'] = jobs.order_by('-created_at')[:5]
        context['upcoming_events'] = events.order_by('date')[:5]
        context['recent_contacts'] = contacts.order_by('-created_at')[:5]
        
        # Add filter options to context
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        context['status_choices'] = JobPosting.STATUS_CHOICES
        
        return context