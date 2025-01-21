from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
import json
import logging
from .models import JobPosting
from .forms import JobPostingForm
from django import template, forms
from .utils.skills_service import SkillsService
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

register = template.Library()

class BaseJobView(LoginRequiredMixin):
    """Base view for job-related operations"""
    model = JobPosting
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).prefetch_related('skills')

class JobListView(BaseJobView, ListView):
    """View for listing job postings"""
    template_name = 'jobs/list.html'
    context_object_name = 'jobs'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = JobPosting.objects.filter(user=self.request.user)
        filter_type = self.request.GET.get('filter', 'all')
        
        match filter_type:
            case 'favorites':
                queryset = queryset.filter(favorites=self.request.user)
            case 'recent':
                one_week_ago = timezone.now() - timedelta(days=7)
                queryset = queryset.filter(created_at__gte=one_week_ago)
            case 'active':
                queryset = queryset.exclude(status__in=['rejected', 'accepted'])
            case 'interviewing':
                queryset = queryset.filter(status='interviewing')
            case 'rejected':
                queryset = queryset.filter(status='rejected')
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fix: Use the correct reverse relationship to get favorited jobs
        context['favorite_job_ids'] = list(
            JobPosting.objects.filter(favorites=self.request.user).values_list('pk', flat=True)
        )
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ['jobs/partials/job_list.html']
        return ['jobs/list.html']

class JobCreateView(BaseJobView, CreateView):
    """View for creating new job postings"""
    form_class = JobPostingForm
    template_name = 'jobs/add.html'
    success_url = reverse_lazy('jobs:list')

    def get(self, request, *args, **kwargs):
        """Handle GET request"""
        logger.debug("GET request received")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request"""
        logger.debug(f"POST request received: {request.POST}")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Handle valid form submission"""
        try:
            # Set the user before saving
            form.instance.user = self.request.user
            self.object = form.save()
            
            # Skills are now handled by Tagulous, no need for manual processing

            # Handle AJAX requests
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Job posting created successfully',
                    'redirect_url': self.get_success_url()
                })
            
            messages.success(self.request, 'Job posting created successfully')
            return super().form_valid(form)
            
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
            raise

    def form_invalid(self, form):
        """Handle invalid form submission"""
        logger.error(f"Form validation failed: {form.errors}")
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Please correct the errors below',
                'errors': form.errors
            }, status=400)
            
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Add additional context if needed"""
        context = super().get_context_data(**kwargs)
        # Get skill groups from SkillsService
        context['skill_icons'] = SkillsService.get_skill_groups()
        return context

class JobPostingUpdateView(BaseJobView, UpdateView):
    """View for updating existing job postings"""
    form_class = JobPostingForm
    template_name = 'jobs/edit.html'
    success_url = reverse_lazy('jobs:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.object
        context['initial_skills'] = json.dumps(list(self.object.skills.values('name', 'icon', 'icon_dark')))
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Job posting updated successfully.')
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object:
            kwargs['initial']['skills'] = self.object.skills.all()
        return kwargs

class JobPostingDeleteView(BaseJobView, DeleteView):
    """View for deleting job postings"""
    template_name = 'jobs/delete.html'
    success_url = reverse_lazy('jobs:list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Job posting deleted successfully.')
        return response

class JobPostingDetailView(BaseJobView, DetailView):
    """View for displaying job details"""
    template_name = 'jobs/detail.html'
    context_object_name = 'job'

class JobFavoritesListView(BaseJobView, ListView):
    """View for displaying user's favorited jobs"""
    template_name = 'jobs/favorites.html'  # Changed from favorite.html
    context_object_name = 'favorite_jobs'

    def get_queryset(self):
        return JobPosting.objects.filter(favorites=self.request.user)  # Make sure this matches your model field name

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)
    if request.user in job.favorites.all():
        job.favorites.remove(request.user)
        is_favorite = False
    else:
        job.favorites.add(request.user)
        is_favorite = True
    
    return HttpResponse(
        status=200,
        headers={
            'HX-Trigger': json.dumps({
                'favoriteToggled': {
                    'jobId': pk,
                    'isFavorite': is_favorite
                }
            })
        }
    )

def skills_autocomplete(request):
    """
    Endpoint for skills autocomplete functionality using SKILL_ICONS
    """
    try:
        query = request.GET.get('q', '').lower()
        all_skills = request.GET.get('all', 'false').lower() == 'true'
        logger.debug(f"Skills autocomplete request - query: {query}, all: {all_skills}")
        
        # Get autocomplete results from SkillsService
        results = SkillsService.get_autocomplete_results(query, all_skills)
        
        return JsonResponse({
            'results': results
        })
        
    except Exception as e:
        logger.exception("Error in skills_autocomplete")
        return JsonResponse({
            'error': str(e),
            'details': 'Server error occurred'
        }, status=500)

@require_http_methods(["POST"])
def parse_job_description(request):
    """Handle job description parsing endpoint"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
    
    text = request.POST.get('description', '').strip()
    if not text:
        return JsonResponse({
            'status': 'error',
            'message': 'No job description provided'
        }, status=400)

    try:
        # Create form instance and parse
        form = JobPostingForm()
        result = form.parse_job_with_ai(text)

        if 'error' in result:
            return JsonResponse({
                'status': 'error',
                'message': result['error']
            }, status=400)

        if 'data' not in result:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid response format'
            }, status=400)

        logger.debug(f"Parsed job data: {result['data']}")
        return JsonResponse({
            'status': 'success',
            'data': result['data']
        })

    except Exception as e:
        logger.exception("Error parsing job description")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def add_job(request):
    """Legacy function for adding jobs - Consider using JobCreateView instead"""
    form = JobPostingForm()
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            messages.success(request, 'Job posting created successfully')
            return redirect('jobs:list')
            
    context = {
        'form': form,
        'skill_icons': SkillsService.get_skill_groups(),
        'icon_name_mapping': json.dumps({}),
        'dark_variants': json.dumps({}),
    }
    return render(request, 'jobs/add.html', context)
