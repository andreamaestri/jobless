from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import JobPosting
from .forms import JobPostingForm


class JobPostingListView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of job postings for the logged-in user.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        ListView: Handles listing of JobPosting objects

    Attributes:
        model: JobPosting model
        template_name: Path to the list template
        context_object_name: Name used for the job list in template context
    """
    model = JobPosting
    template_name = 'jobs/list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return JobPosting.objects.filter(user=self.request.user)


class JobPostingCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new job posting entries.

    Inherits from:
        LoginRequiredMixin: Ensures user authentication
        CreateView: Handles creation of JobPosting objects

    Attributes:
        model: JobPosting model
        form_class: Form class for job posting creation
        template_name: Path to the creation template
        success_url: URL to redirect to after successful creation
    """
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/add.html'
    success_url = reverse_lazy('jobs:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Job posting added successfully.')
        return super().form_valid(form)


class JobPostingUpdateView(LoginRequiredMixin, UpdateView):
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
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/edit.html'
    success_url = reverse_lazy('jobs:list')

    def get_queryset(self):
        # Ensure users can only edit their own job postings
        return JobPosting.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Job posting updated successfully.')
        return super().form_valid(form)


class JobPostingDeleteView(LoginRequiredMixin, DeleteView):
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
    model = JobPosting
    template_name = 'jobs/delete.html'
    success_url = reverse_lazy('jobs:list')

    def get_queryset(self):
        # Ensure users can only delete their own job postings
        return JobPosting.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Job posting deleted successfully.')
        return super().delete(request, *args, **kwargs)


class JobPostingDetailView(LoginRequiredMixin, DetailView):
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
    model = JobPosting
    template_name = 'jobs/detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        # Ensure users can only view their own job postings
        return JobPosting.objects.filter(user=self.request.user)
    
def toggle_favourite(request, job_id):
    """Toggle favourite status of a job posting"""
    job = get_object_or_404(JobPosting, id=job_id)
    
    if request.method == "POST":
        if request.user in job.favourites.all():
            job.favourites.remove(request.user)
            messages.success(request, "Job removed from favourites!")
        else:
            job.favourites.add(request.user)
            messages.success(request, "Job added to favourites!")
    
    return redirect("jobs:list")


def favourited_jobs(request):
    """Display user's favourited jobs"""
    favorite_jobs = JobPosting.objects.filter(favourites=request.user)
    return render(request, "jobs/favourites.html", {"favorite_jobs": favorite_jobs})
