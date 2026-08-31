from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from openai import OpenAI
import json

from .models import JobPosting, SkillTreeModel
from .forms import JobPostingForm
from .components.job_list_component import JobListComponent
from .components.job_detail_component import JobDetailComponent


def api_skills(request):
    """API endpoint to get all skills"""
    skills = SkillTreeModel.objects.values('id', 'name', 'label', 'icon')
    return JsonResponse({'skills': list(skills)})


def skills_autocomplete(request):
    """Endpoint for skill autocomplete suggestions"""
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    skills = SkillTreeModel.objects.filter(
        Q(name__icontains=query) | Q(label__icontains=query)
    )[:10]
    results = [{
        'name': skill.name,
        'label': skill.label,
        'icon': skill.get_icon()
    } for skill in skills]
    return JsonResponse({'results': results})


@login_required
def parse_job_description(request):
    """Endpoint to parse job descriptions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    description = request.POST.get('description', '')
    if not description:
        return JsonResponse({'error': 'No description provided'}, status=400)
        
    if not getattr(settings, 'GEMINI_API_KEY', None):
        return JsonResponse({'error': 'AI ist derzeit nicht konfiguriert.'}, status=503)

    prompt = """Extract structured job posting data from the text below. Return only valid JSON with
these keys: title, company, location, salary_range, url, description, skills.
Use empty strings for unknown text fields and an array of concise skill names for skills.
Do not invent information. Preserve the complete original description in description.

JOB POSTING:
""" + description[:12000]

    try:
        response = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=settings.GEMINI_API_KEY,
            timeout=60,
            max_retries=1,
        ).chat.completions.create(
            model=getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash'),
            messages=[
                {'role': 'system', 'content': 'You extract job posting data accurately.'},
                {'role': 'user', 'content': prompt},
            ],
            response_format={'type': 'json_object'},
            temperature=0,
        )
        content = response.choices[0].message.content or '{}'
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError('AI response was not an object')
        return JsonResponse(parsed)
    except (json.JSONDecodeError, ValueError, IndexError, KeyError) as exc:
        return JsonResponse({'error': f'AI-Antwort konnte nicht verarbeitet werden: {exc}'}, status=502)
    except Exception:
        return JsonResponse({'error': 'Die Stellenausschreibung konnte nicht verarbeitet werden.'}, status=502)


class JobListView(LoginRequiredMixin, ListView):
    template_name = 'jobs/list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        filter_param = self.request.GET.get('filter', 'all')
        jobs = JobPosting.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
        
        if filter_param == 'favorites':
            jobs = jobs.filter(favorited_by=self.request.user)
        elif filter_param == 'recent':
            jobs = jobs.order_by('-updated_at')[:10]
        elif filter_param == 'active':
            jobs = jobs.filter(status__in=['APPLIED', 'INTERVIEWING'])
        elif filter_param == 'interviewing':
            jobs = jobs.filter(status='INTERVIEWING')
            
        return jobs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorite_job_ids = []
        if self.request.user.is_authenticated:
            favorite_job_ids = list(
                self.request.user.favorited_jobs.values_list('id', flat=True)
            )
        
        job_list_component = JobListComponent()
        component_context = job_list_component.get_context_data(
            jobs=context['jobs'],
            favorite_job_ids=favorite_job_ids
        )
        context.update(component_context)
        return context


class JobPostingDetailView(LoginRequiredMixin, DetailView):
    model = JobPosting
    template_name = 'jobs/detail.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_favorite = self.request.user in context['job'].favorited_by.all()
        
        job_detail_component = JobDetailComponent()
        component_context = job_detail_component.get_context_data(
            job=context['job'],
            is_favorite=is_favorite
        )
        context.update(component_context)
        return context


class JobCreateView(LoginRequiredMixin, CreateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/add.html'
    success_url = reverse_lazy('jobs:list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Job added successfully.')
        return response


class JobPostingUpdateView(LoginRequiredMixin, UpdateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/edit.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Job updated successfully.')
        return response


class JobPostingDeleteView(LoginRequiredMixin, DeleteView):
    model = JobPosting
    success_url = reverse_lazy('jobs:list')
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Job deleted successfully.')
        return super().delete(request, *args, **kwargs)


class JobFavoritesView(LoginRequiredMixin, ListView):
    template_name = 'jobs/list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        return JobPosting.objects.filter(favorited_by=self.request.user)


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        job = get_object_or_404(JobPosting, pk=pk)
        if job.toggle_favorite(request.user):
            messages.success(request, 'Job added to favorites.')
        else:
            messages.success(request, 'Job removed from favorites.')
        return HttpResponseRedirect(
            request.META.get('HTTP_REFERER', reverse('jobs:list'))
        )
