from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.utils import timezone
from django.urls import reverse  # Add this import
from datetime import timedelta
from jobs.models import JobPosting
from events.models import Event
from contacts.models import Contact
from .forms import SearchFilterForm

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home/home.html"

    def get_active_jobs_count(self, jobs):
        """Count jobs that are either 'interested', 'applied', or 'interviewing'"""
        return jobs.filter(status__in=['interested', 'applied', 'interviewing']).count()

    def get_upcoming_events_count(self, events):
        """Count events in the next 7 days"""
        now = timezone.now()
        week_later = now + timedelta(days=7)
        return events.filter(date__range=[now, week_later]).count()

    def calculate_success_rate(self, jobs):
        """Calculate interview success rate"""
        total_applications = jobs.filter(status__in=['applied', 'interviewing', 'offered', 'rejected']).count()
        if total_applications == 0:
            return 0
        successful = jobs.filter(status__in=['interviewing', 'offered']).count()
        return round((successful / total_applications) * 100) if total_applications > 0 else 0

    def get_job_status_chart_data(self, jobs):
        """Get job status data for charts"""
        status_counts = dict(jobs.values_list('status').annotate(count=Count('status')))
        colors = {
            'interested': '#36D399',  # success
            'applied': '#3ABFF8',     # primary
            'interviewing': '#FBBD23', # warning
            'rejected': '#F87272',     # error
            'offered': '#6419E6',      # secondary
        }
        return {
            'labels': list(status_counts.keys()),
            'data': list(status_counts.values()),
            'colors': [colors.get(status, '#666') for status in status_counts.keys()]
        }

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

        # Calculate statistics
        context['active_jobs_count'] = self.get_active_jobs_count(jobs)
        context['upcoming_events_count'] = self.get_upcoming_events_count(events)
        context['total_contacts'] = contacts.count()
        context['success_rate'] = self.calculate_success_rate(jobs)
            
        # Add to context with ordering
        context['recent_jobs'] = jobs.order_by('-updated_at')[:5]
        context['upcoming_events'] = events.filter(
            date__gte=timezone.now()
        ).order_by('date')[:5]
        context['recent_contacts'] = contacts.order_by('-created_at')[:5]
        
        # Add filter options to context
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        context['status_choices'] = JobPosting.STATUS_CHOICES

        # Add total jobs count for percentage calculations
        context['total_jobs'] = jobs.count()

        # Add job status counts for potential chart/stats
        status_counts = dict(jobs.values_list('status').annotate(count=Count('status')))
        context['status_counts'] = status_counts

        # Add chart data
        context['job_status_chart'] = self.get_job_status_chart_data(jobs)
        
        # Add activity timeline
        context['recent_activity'] = self.get_recent_activity()
        
        # Add cards data
        context['cards'] = [
            {
                'title': 'Recent Jobs',
                'subtitle': 'Track your applications',
                'items': context['recent_jobs'],
                'headers': ['Title', 'Company', 'Location', 'Status', 'Updated'],
                'empty_icon': 'octicon:briefcase-16',
                'empty_message': 'No jobs added yet',
                'empty_button': 'Add Your First Job',
                'add_url': reverse('jobs:add'),
                'view_all_url': reverse('jobs:list'),
            },
            {
                'title': 'Upcoming Events',
                'subtitle': 'Your scheduled interviews and meetings',
                'items': context['upcoming_events'],
                'headers': ['Title', 'Type', 'Date & Time', 'Location'],
                'empty_icon': 'octicon:calendar-16',
                'empty_message': 'No upcoming events',
                'empty_button': 'Add Your First Event',
                'add_url': reverse('events:add'),
                'view_all_url': reverse('events:list'),
            },
            {
                'title': 'Recent Contacts',
                'subtitle': 'Your professional network',
                'items': context['recent_contacts'],
                'headers': ['Name', 'Company', 'Position', 'Email', 'Phone'],
                'empty_icon': 'octicon:people-16',
                'empty_message': 'No contacts added yet',
                'empty_button': 'Add Your First Contact',
                'add_url': reverse('contacts:add'),
                'view_all_url': reverse('contacts:list'),
            }
        ]
        
        # Add search form to context
        initial_data = {
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'type': self.request.GET.get('type', '')
        }
        context['search_form'] = SearchFilterForm(initial=initial_data)
        
        return context

    def get_recent_activity(self):
        """Get recent activity across all models"""
        recent = []
        user = self.request.user
        
        # Get recent jobs
        jobs = JobPosting.objects.filter(user=user).order_by('-updated_at')[:5]
        for job in jobs:
            recent.append({
                'type': 'job',
                'action': f"Updated job application for {job.title}",
                'date': job.updated_at,
                'url': job.get_absolute_url()
            })
        
        # Get recent events
        events = Event.objects.filter(user=user).order_by('-created_at')[:5]
        # ...similar for events and contacts...
        
        return sorted(recent, key=lambda x: x['date'], reverse=True)[:5]