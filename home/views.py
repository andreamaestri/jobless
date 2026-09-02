from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from jobs.models import JobPosting
from events.models import Event
from contacts.models import Contact


@login_required
def api_search(request):
    """Global search API for the dashboard search modal.

    Searches the current user's jobs, events, and contacts and returns
    at most eight combined results as JSON.
    """
    query = request.GET.get("q", "").strip()

    if not query or len(query) < 2:
        return JsonResponse([], safe=False)

    results = []

    jobs = JobPosting.objects.filter(user=request.user).filter(
        Q(title__icontains=query) | Q(company__icontains=query)
    )[:8]
    for job in jobs:
        results.append({
            "icon": "octicon:briefcase-24",
            "title": job.title,
            "subtitle": job.company,
            "url": reverse("jobs:detail", args=[job.pk]),
        })

    events = Event.objects.filter(user=request.user).filter(
        Q(title__icontains=query) | Q(location__icontains=query)
    )[:8]
    for event in events:
        results.append({
            "icon": "octicon:calendar-24",
            "title": event.title,
            "subtitle": event.location,
            "url": reverse("events:detail", args=[event.pk]),
        })

    contacts = Contact.objects.filter(user=request.user).filter(
        Q(name__icontains=query)
        | Q(company__icontains=query)
        | Q(email__icontains=query)
    )[:8]
    for contact in contacts:
        results.append({
            "icon": "octicon:person-24",
            "title": contact.name,
            "subtitle": contact.company or contact.email,
            "url": reverse("contacts:detail", args=[contact.pk]),
        })

    return JsonResponse(results[:8], safe=False)

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
        """Calculate interview success rate."""
        total_applications = jobs.filter(
            status__in=['applied', 'interviewing', 'rejected', 'accepted']
        ).count()
        if total_applications == 0:
            return 0
        successful = jobs.filter(status__in=['interviewing', 'accepted']).count()
        return round((successful / total_applications) * 100)

    def get_greeting(self):
        """Return a time-of-day greeting."""
        hour = timezone.localtime().hour
        if hour < 12:
            return _("Good morning")
        if hour < 18:
            return _("Good afternoon")
        return _("Good evening")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Base querysets filtered by user
        jobs = JobPosting.objects.filter(user=self.request.user)
        events = Event.objects.filter(user=self.request.user)
        contacts = Contact.objects.filter(user=self.request.user)

        # Calculate statistics
        context['active_jobs_count'] = self.get_active_jobs_count(jobs)
        context['upcoming_events_count'] = self.get_upcoming_events_count(events)
        context['total_contacts'] = contacts.count()
        context['success_rate'] = self.calculate_success_rate(jobs)
        context['total_applications'] = jobs.filter(
            status__in=['applied', 'interviewing', 'rejected', 'accepted']
        ).count()
        context['greeting'] = self.get_greeting()

        # Add to context with ordering
        context['recent_jobs'] = jobs.order_by('-updated_at')[:5]
        context['upcoming_events'] = events.filter(
            date__gte=timezone.now()
        ).order_by('date')[:5]
        context['recent_contacts'] = contacts.order_by('-created_at')[:5]

        # Add total jobs count for percentage calculations
        context['total_jobs'] = jobs.count()

        # Add job status counts for stats
        status_counts = dict(jobs.values_list('status').annotate(count=Count('status')))
        context['status_counts'] = status_counts

        # Ordered status rows for the progress card
        total = context['total_jobs']
        context['status_rows'] = [
            {
                'key': key,
                'label': label,
                'count': status_counts.get(key, 0),
                'pct': round(status_counts.get(key, 0) / total * 100) if total else 0,
            }
            for key, label in JobPosting.STATUS_CHOICES
        ]

        return context