from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required  # Add this import
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
from .models import JobPosting, SKILL_ICONS  # Remove Skill import
from .forms import JobPostingForm
from django import template, forms
from .utils.skill_icons import DARK_VARIANTS, ICON_NAME_MAPPING

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
            
            # Handle skills if present
            skills = self.request.POST.get('required_skills')
            if skills:
                try:
                    # Parse the JSON string into a list
                    skills_data = json.loads(skills)
                    # Extract just the skill names
                    skill_names = [skill['name'] for skill in skills_data]
                    # Set the skills
                    self.object.required_skills.set(skill_names)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing skills JSON: {e}")
                    raise

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
        # Group skills by first letter using both SKILL_ICONS and ICON_NAME_MAPPING
        skill_groups = {}
        
        # Add skills from SKILL_ICONS
        for icon, name in SKILL_ICONS:
            first_letter = name[0].upper()
            if first_letter not in skill_groups:
                skill_groups[first_letter] = []
                
            # Get the formatted icon
            formatted_icon = icon
            if icon in DARK_VARIANTS:
                dark_icon = DARK_VARIANTS[icon]
            else:
                # Check if the icon exists in the mapping
                mapped_icon = ICON_NAME_MAPPING.get(name, icon)
                dark_icon = DARK_VARIANTS.get(mapped_icon, mapped_icon)
                
            skill_groups[first_letter].append({
                'name': name,
                'icon': formatted_icon,
                'icon_dark': dark_icon
            })

        # Convert to sorted list of groups
        context['skill_icons'] = [
            {
                'letter': letter,
                'skills': sorted(skills, key=lambda x: x['name'])
            }
            for letter, skills in sorted(skill_groups.items())
        ]
        
        # Add both mappings to the context
        context['icon_name_mapping'] = json.dumps(ICON_NAME_MAPPING)
        context['dark_variants'] = json.dumps(DARK_VARIANTS)
        return context

class JobPostingUpdateView(BaseJobView, UpdateView):
    """View for updating existing job postings"""
    form_class = JobPostingForm
    template_name = 'jobs/edit.html'
    success_url = reverse_lazy('jobs:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Job posting updated successfully.')
        return response

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
    """View for displaying user's favourited jobs"""
    template_name = 'jobs/favourites.html'
    context_object_name = 'favorite_jobs'

    def get_queryset(self):
        return JobPosting.objects.filter(favourites=self.request.user)

# Remove or comment out the old function-based view:
# def favourited_jobs(request):
#     """Display user's favourited jobs"""
#     favorite_jobs = JobPosting.objects.filter(favourites=request.user)
#     return render(request, "jobs/favourites.html", {"favorite_jobs": favorite_jobs})

@login_required
def toggle_favourite(request, job_id):
    """Toggle favourite status of a job posting"""
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
        
    job = get_object_or_404(JobPosting, id=job_id)
    
    if request.user in job.favourites.all():
        job.favourites.remove(request.user)
        message = "Job removed from favourites"
    else:
        job.favourites.add(request.user)
        message = "Job added to favourites"
    
    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=200,
            headers={'HX-Trigger': json.dumps({'showMessage': {'message': message}})}
        )
        
    messages.success(request, message)
    return redirect("jobs:list")

def skills_autocomplete(request):
    """
    Endpoint for skills autocomplete functionality using SKILL_ICONS
    """
    try:
        query = request.GET.get('q', '').lower()
        all_skills = request.GET.get('all', 'false').lower() == 'true'
        logger.debug(f"Skills autocomplete request - query: {query}, all: {all_skills}")
        
        # Use SKILL_ICONS directly
        skills_data = list(SKILL_ICONS)  # Convert to list to ensure it's mutable
        
        # Filter if there's a query and not requesting all
        if query and not all_skills:
            skills_data = [
                (icon, name) for icon, name in skills_data 
                if query.lower() in name.lower()
            ]
        
        # Group skills by first letter with proper icon handling
        grouped_skills = {}
        for icon, name in skills_data:
            first_letter = name[0].upper()
            if first_letter not in grouped_skills:
                grouped_skills[first_letter] = []
            
            # Ensure proper icon formatting
            icon_name = icon.replace('skill-icons:', '')
            formatted_icon = f"skill-icons:{icon_name}"
            dark_icon = DARK_VARIANTS.get(formatted_icon, formatted_icon)
            
            grouped_skills[first_letter].append({
                'name': name,
                'icon': formatted_icon,
                'icon_dark': dark_icon
            })
        
        # Convert to sorted list of groups
        results = [
            {
                'letter': letter,
                'skills': sorted(grouped_skills[letter], key=lambda x: x['name'].upper())
            }
            for letter in sorted(grouped_skills.keys())
        ]
        
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
