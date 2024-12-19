import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect  # unused right now
from .models import Event
from .forms import EventForm
from django.http import JsonResponse
from django.utils.formats import date_format


class EventListView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of events for the logged-in user.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        ListView: Handles listing of Event objects

    Attributes:
        model: Event model
        template_name: Path to the list template
        context_object_name: Name used for the event list in template context
    """
    model = Event
    template_name = 'events/list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events_json = json.dumps(
            list(self.get_queryset().values('title', 'start_date', 'end_date')),
            cls=DjangoJSONEncoder
        )
        context['events_json'] = events_json
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/add.html'
    success_url = reverse_lazy('events:list')

    def get_form_kwargs(self):
        """Add the logged-in user to the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Event added successfully.')
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/edit.html'
    success_url = reverse_lazy('events:list')

    def get_form_kwargs(self):
        """Add the logged-in user to the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        # Ensure users can only edit their own events
        return Event.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully.')
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting event entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        DeleteView: Handles deletion of Event objects

    Attributes:
        model: Event model
        template_name: Path to the deletion confirmation template
        success_url: URL to redirect to after successful deletion
    """
    model = Event
    template_name = 'events/delete.html'
    success_url = reverse_lazy('events:list')

    def get_queryset(self):
        # Ensure users can only delete their own events
        return Event.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Event deleted successfully.')
        return super().delete(request, *args, **kwargs)


class EventDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying detailed information about an event.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        DetailView: Handles displaying detailed view of Event objects

    Attributes:
        model: Event model
        template_name: Path to the detail template
        context_object_name: Name used for the event in template context
    """
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        # Ensure users can only view their own events
        return Event.objects.filter(user=self.request.user)
    
class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'events/calendar.html'

def calendar_events(request):
    """Return events in format required by FullCalendar."""
    if not request.user.is_authenticated:
        return JsonResponse({'events': []})
    
    events = Event.objects.filter(user=request.user)
    event_list = []
    
    for event in events:
        event_data = {
            'id': event.id,
            'title': event.title,
            'start': event.date.isoformat(),
            'type': event.event_type,
            'className': f'event-type-{event.event_type}',
            'extendedProps': {
                'type': event.get_event_type_display(),
                'location': event.location,
            }
        }
        
        event_list.append(event_data)
    
    return JsonResponse(event_list, safe=False)