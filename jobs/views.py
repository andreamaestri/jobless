import logging
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.core.exceptions import ValidationError
from django.views import View

from .forms import JobPostingForm
from .models import JobPosting
from .utils.skills_service import SkillsService
from .utils.skill_icons import (
    SKILL_ICONS,
    DARK_VARIANTS,
    ICON_NAME_MAPPING,
    get_icon_variant,
)
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


class BaseJobView(LoginRequiredMixin):
    """Base view for job-related operations"""

    model = JobPosting

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .prefetch_related("skills")
        )


class JobListView(BaseJobView, ListView):
    """View for listing job postings"""

    template_name = "jobs/list.html"
    context_object_name = "jobs"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = JobPosting.objects.filter(user=self.request.user)
        filter_type = self.request.GET.get("filter", "all")

        match filter_type:
            case "recent":
                one_week_ago = timezone.now() - timedelta(days=7)
                queryset = queryset.filter(created_at__gte=one_week_ago)
            case "active":
                queryset = queryset.exclude(status__in=["rejected", "accepted"])
            case "interviewing":
                queryset = queryset.filter(status="interviewing")
            case "rejected":
                queryset = queryset.filter(status="rejected")

        return queryset.order_by("-created_at").select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class JobCreateView(BaseJobView, CreateView):
    """View for creating new job postings"""

    form_class = JobPostingForm
    template_name = "jobs/add.html"
    success_url = reverse_lazy("jobs:list")

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
            if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Job posting created successfully",
                        "redirect_url": self.get_success_url(),
                    }
                )

            messages.success(self.request, "Job posting created successfully")
            return super().form_valid(form)

        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": str(e)}, status=500)
            raise

    def form_invalid(self, form):
        """Handle invalid form submission"""
        logger.error(f"Form validation failed: {form.errors}")

        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Please correct the errors below",
                    "errors": form.errors,
                },
                status=400,
            )

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Add additional context if needed"""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "skill_icons": SkillsService.get_skill_groups(),
                "icon_name_mapping": mark_safe(json.dumps(ICON_NAME_MAPPING)),
                "dark_variants": mark_safe(json.dumps(DARK_VARIANTS)),
                "default_icon": "heroicons:academic-cap",
            }
        )
        return context


class JobPostingUpdateView(BaseJobView, UpdateView):
    """View for updating existing job postings"""

    form_class = JobPostingForm
    template_name = "jobs/edit.html"
    success_url = reverse_lazy("jobs:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job"] = self.object
        context["initial_skills"] = json.dumps(
            list(self.object.skills.values("name", "icon", "icon_dark"))
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Job posting updated successfully.")
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object:
            kwargs["initial"]["skills"] = self.object.skills.all()
        return kwargs


class JobPostingDeleteView(BaseJobView, DeleteView):
    """View for deleting job postings"""

    template_name = "jobs/delete.html"
    success_url = reverse_lazy("jobs:list")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, "Job posting deleted successfully.")
        return response


class JobPostingDetailView(BaseJobView, DetailView):
    """View for displaying job details"""

    template_name = "jobs/detail.html"
    context_object_name = "job"


class JobFavoritesView(BaseJobView, ListView):
    """View for listing favorite job postings"""
    template_name = "jobs/favorites.html"
    context_object_name = "jobs"

    def get_queryset(self):
        return JobPosting.objects.filter(
            jobfavorite__user=self.request.user
        ).distinct().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_favorites_page'] = True
        context['favorite_job_ids'] = list(
            JobFavorite.objects.filter(
                user=self.request.user
            ).values_list('job_id', flat=True)
        )
        return context


def skills_autocomplete(request):
    """
    Endpoint for skills autocomplete functionality using SKILL_ICONS
    """
    try:
        query = request.GET.get("q", "").lower()
        all_skills = request.GET.get("all", "false").lower() == "true"
        logger.debug(f"Skills autocomplete request - query: {query}, all: {all_skills}")

        # Get autocomplete results from SkillsService
        results = SkillsService.get_autocomplete_results(query, all_skills)

        return JsonResponse({"results": results})

    except Exception as e:
        logger.exception("Error in skills_autocomplete")
        return JsonResponse(
            {"error": str(e), "details": "Server error occurred"}, status=500
        )


@require_POST
@login_required
def parse_job_description(request):
    """Parse job description using AI and return structured data."""
    try:
        description = request.POST.get("description", "").strip()
        if not description:
            return JsonResponse(
                {"status": "error", "error": "No description provided"}, status=400
            )

        # Get form instance for parsing
        form = JobPostingForm()
        result = form.parse_job_with_ai(description)

        # If parsing failed
        if "error" in result:
            logger.error(f"AI parsing error: {result['error']}")
            return JsonResponse({"status": "error", "error": result["error"]}, status=400)

        # Validate required fields
        required_fields = ["title", "company", "location"]
        missing_fields = [
            field
            for field in required_fields
            if not result.get("data", {}).get(field)
        ]

        if missing_fields:
            error_msg = f"AI couldn't extract these required fields: {', '.join(missing_fields)}"
            logger.error(f"Missing required fields: {missing_fields}")
            return JsonResponse(
                {
                    "status": "error",
                    "error": error_msg,
                    "missing_fields": missing_fields,
                },
                status=400,
            )

        # All required fields present, return success
        return JsonResponse({"status": "success", "data": result["data"]})

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return JsonResponse({"status": "error", "error": str(e)}, status=400)

    except Exception as e:
        logger.exception("Unexpected error in parse_job_description")
        return JsonResponse(
            {
                "status": "error",
                "error": "An unexpected error occurred while processing the job description",
            },
            status=500,
        )


def add_job(request):
    """Legacy function for adding jobs - Consider using JobCreateView instead"""
    form = JobPostingForm()
    if request.method == "POST":
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            messages.success(request, "Job posting created successfully")
            return redirect("jobs:list")

    context = {
        "form": form,
        "skill_icons": SkillsService.get_skill_groups(),
        "icon_name_mapping": json.dumps({}),
        "dark_variants": json.dumps({}),
    }
    return render(request, "jobs/add.html", context)


from .utils.skill_icons import ICON_NAME_MAPPING, DARK_VARIANTS


def get_skills_data(request):
    # Convert tuple of (icon, name) pairs into a dictionary structure
    all_skills = [
        {"name": name, "icon": icon, "icon_dark": DARK_VARIANTS.get(icon, icon)}
        for icon, name in SKILL_ICONS
    ]

    # Sort skills by name and group them alphabetically
    sorted_skills = sorted(all_skills, key=lambda x: x["name"])
    grouped_skills = {}

    for skill in sorted_skills:
        first_letter = skill["name"][0].upper()
        if first_letter not in grouped_skills:
            grouped_skills[first_letter] = []
        grouped_skills[first_letter].append(skill)

    # Convert to list of groups for template
    skill_icons = [
        {"letter": letter, "skills": skills}
        for letter, skills in sorted(grouped_skills.items())
    ]

    context = {
        "skill_icons": skill_icons,
        "icon_name_mapping": json.dumps(ICON_NAME_MAPPING),
        "dark_variants": json.dumps(DARK_VARIANTS),
    }

    return context


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            job = get_object_or_404(JobPosting, pk=pk)
            is_favorite = job.toggle_favorite(request.user)
            
            return JsonResponse({
                'status': 'success',
                'is_favorite': is_favorite
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

# ...remove or comment out the old toggle_favorite function and job_list view...