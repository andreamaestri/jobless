from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect  # unused right now
from .models import Event
from .forms import EventForm


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


class EventCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new event entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        CreateView: Handles creation of Event objects

    Attributes:
        model: Event model
        form_class: Form class for event creation
        template_name: Path to the creation template
        success_url: URL to redirect to after successful creation
    """
    model = Event
    form_class = EventForm
    template_name = 'events/add.html'
    success_url = reverse_lazy('events:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Event added successfully.')
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating existing event entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        UpdateView: Handles updating of Event objects

    Attributes:
        model: Event model
        form_class: Form class for event updating
        template_name: Path to the edit template
        success_url: URL to redirect to after successful update
    """
    model = Event
    form_class = EventForm
    template_name = 'events/edit.html'
    success_url = reverse_lazy('events:list')

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