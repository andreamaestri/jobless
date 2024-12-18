from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from jobs.models import JobPosting
from events.models import Event
from contacts.models import Contact

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_jobs'] = JobPosting.objects.filter(
            user=self.request.user).order_by('-created_at')[:5]
        context['upcoming_events'] = Event.objects.filter(
            user=self.request.user).order_by('date')[:5]
        context['recent_contacts'] = Contact.objects.filter(
            user=self.request.user).order_by('-created_at')[:5]
        return context