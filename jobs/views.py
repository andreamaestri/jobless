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
from .models import JobPosting, SKILL_ICONS
from .forms import JobPostingForm
from django import template, forms
from .utils.skill_icons import DARK_VARIANTS, ICON_NAME_MAPPING

logger = logging.getLogger(__name__)

register = template.Library()

class BaseJobView(LoginRequiredMixin):
    """Base view for job-related operations"""
    model = JobPosting
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

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
        context['skill_icons'] = self._get_grouped_skills()
        return context

    def _get_grouped_skills(self):
        """Helper method to group skills"""
        skill_groups = {}
        for icon, name in SKILL_ICONS:
            first_letter = name[0].upper()
            if first_letter not in skill_groups:
                skill_groups[first_letter] = []
            
            skill_groups[first_letter].append({
                'name': name,
                'icon': ICON_NAME_MAPPING.get(name, icon),
                'icon_dark': DARK_VARIANTS.get(
                    ICON_NAME_MAPPING.get(name, icon),
                    ICON_NAME_MAPPING.get(name, icon)
                )
            })
        
        return [
            {
                'letter': letter,
                'skills': sorted(skills, key=lambda x: x['name'].upper())
            }
            for letter, skills in sorted(skill_groups.items())
        ]

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
    """Handle skills autocomplete API requests"""
    query = request.GET.get('q', '').lower()
    all_param = request.GET.get('all', 'false').lower() == 'true'
    
    # Get all skills with proper icon mapping
    skills_data = []
    for icon, name in SKILL_ICONS:
        if not query or query in name.lower():
            mapped_icon = ICON_NAME_MAPPING.get(name, icon)
            dark_icon = DARK_VARIANTS.get(mapped_icon, mapped_icon)
            skills_data.append({
                'name': name,
                'icon': mapped_icon,
                'icon_dark': dark_icon,
                'value': name
            })
    
    # Always group by first letter when all=true, otherwise only when no query
    if all_param or not query:
        grouped_data = {}
        for skill in skills_data:
            first_letter = skill['name'][0].upper()
            if first_letter not in grouped_data:
                grouped_data[first_letter] = []
            grouped_data[first_letter].append(skill)
        
        # Sort groups and skills within groups
        results = []
        for letter in sorted(grouped_data.keys()):
            letter_group = sorted(grouped_data[letter], key=lambda x: x['name'])
            if all_param:
                # Return in the same format as the modal
                results.append({
                    'letter': letter,
                    'skills': letter_group
                })
            else:
                results.extend(letter_group)
    else:
        results = sorted(skills_data, key=lambda x: x['name'])
    
    return JsonResponse({'results': results})

# Remove get_skills_data as it's no longer needed

@require_http_methods(["POST"])
def parse_job_description(request):
    """Handle job description parsing endpoint"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
    
    text = request.POST.get('paste', '').strip()
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
