from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Contact
from .forms import ContactForm  # We'll need to create this


class ContactListView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of job postings for the logged-in user.  THESE DOCSTRINGS NEED CHANGING TO CONTACT

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        ListView: Handles listing of JobPosting objects

    Attributes:
        model: JobPosting model
        template_name: Path to the list template
        context_object_name: Name used for the job list in template context
    """
    model = Contact
    template_name = 'contacts/list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class ContactCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new Contact.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        CreateView: Handles creation of JobPosting objects

    Attributes:
        model: JobPosting model
        form_class: Form class for job posting creation
        template_name: Path to the creation template
        success_url: URL to redirect to after successful creation
    """
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/add.html'
    success_url = reverse_lazy('contacts:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Contact added successfully.')
        return super().form_valid(form)


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating existing job posting entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        UpdateView: Handles updating of JobPosting objects

    Attributes:
        model: JobPosting model
        form_class: Form class for job posting updating
        template_name: Path to the edit template
        success_url: URL to redirect to after successful update
    """
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/edit.html'
    success_url = reverse_lazy('contacts:list')

    def get_queryset(self):
        # Ensure users can only edit their own job postings
        return Contact.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Contact updated successfully.')
        return super().form_valid(form)


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting job posting entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        DeleteView: Handles deletion of JobPosting objects

    Attributes:
        model: JobPosting model
        template_name: Path to the deletion confirmation template
        success_url: URL to redirect to after successful deletion
    """
    model = Contact
    template_name = 'contacts/delete.html'
    success_url = reverse_lazy('contacts:list')

    def get_queryset(self):
        # Ensure users can only delete their own job postings
        return Contact.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Contact deleted successfully.')
        return super().delete(request, *args, **kwargs)


class ContactDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying detailed information about a job posting.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        DetailView: Handles displaying detailed view of JobPosting objects

    Attributes:
        model: JobPosting model
        template_name: Path to the detail template
        context_object_name: Name used for the job posting in template context
    """
    model = Contact
    template_name = 'contacts/detail.html'
    context_object_name = 'contact'

    def get_queryset(self):
        # Ensure users can only view their own job postings
        return Contact.objects.filter(user=self.request.user)