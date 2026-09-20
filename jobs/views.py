from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
    View,
)
from django.views.generic.edit import FormMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import gettext as _
from openai import OpenAI
import json
from datetime import date, timedelta

from .models import (
    JobPosting,
    SkillTreeModel,
    UserProfile,
    ObligationPlan,
    Application,
    EvidenceFile,
    Submission,
    Vermittlungsvorschlag,
    Absence,
    Obstacle,
)
from events.models import Event
from . import pdf as nachweis_pdf
from . import exports as nachweis_exports
from .forms import JobPostingForm
from .components.job_list_component import JobListComponent
from .components.job_detail_component import JobDetailComponent


EXPORT_PROFILES = {
    "BA_MINIMAL": _("BA-Minimal (official form orientation)"),
    "JOBCENTER_LIST": _("Jobcenter list"),
    "CUSTOM_COLUMNS": _("Consultation overview (internal)"),
    "KOSTENBELEG": _("Costs of efforts (Kostenbeleg)"),
}

def _get_profile(user):
    profile, _created = UserProfile.objects.get_or_create(user=user)
    return profile

def _get_active_plan(user):
    return (
        ObligationPlan.objects.filter(user=user, is_active=True)
        .order_by("-valid_from", "-created_at")
        .first()
    )

def _parse_period(request, default_month=None):
    """Return (start, end, label) from GET params: month / rolling / custom."""
    month = request.GET.get("month") or default_month
    if request.GET.get("period") == "rolling":
        end = date.today()
        return end - timedelta(days=29), end, _("Last 30 days")
    if request.GET.get("period") == "custom":
        try:
            start = date.fromisoformat(request.GET.get("start"))
            end = date.fromisoformat(request.GET.get("end"))
            return start, end, f"{start:%d.%m.%Y} – {end:%d.%m.%Y}"
        except (ValueError, TypeError):
            pass
    if month:
        try:
            year, mon = (int(part) for part in month.split("-"))
            start = date(year, mon, 1)
            if mon == 12:
                end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(year, mon + 1, 1) - timedelta(days=1)
            return start, end, start.strftime("%Y-%m")
        except (ValueError, TypeError):
            pass
    today = date.today()
    start = today.replace(day=1)
    if today.month == 12:
        end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    return start, end, start.strftime("%Y-%m")

def _nachweisbar_qs(user, start, end):
    return Application.objects.filter(
        user=user,
        applied_on__gte=start,
        applied_on__lte=end,
    ).exclude(job_title="").exclude(employer_name="").order_by("applied_on")

def _export_profile(request):
    raw = request.GET.get("profile", "")
    return raw if raw in EXPORT_PROFILES else nachweis_pdf.JOBCENTER_LIST

def api_skills(request):
    """API endpoint to get all skills"""
    skills = [
        {
            **skill.to_dict(),
            'icon': skill.get_icon(),
        }
        for skill in SkillTreeModel.objects.all()
    ]
    return JsonResponse({'skills': skills})


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
        skill_name = self.request.GET.get('skill', '')
        jobs = JobPosting.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
        
        if filter_param == 'favorites':
            jobs = jobs.filter(favorites=self.request.user).distinct()
        elif filter_param == 'recent':
            jobs = jobs.order_by('-updated_at')[:10]
        elif filter_param == 'active':
            jobs = jobs.filter(status__in=['applied', 'interviewing'])
        elif filter_param == 'interviewing':
            jobs = jobs.filter(status='interviewing')
        elif filter_param == 'applied':
            jobs = jobs.filter(status='applied')
        elif filter_param == 'rejected':
            jobs = jobs.filter(status='rejected')
        elif filter_param == 'accepted':
            jobs = jobs.filter(status='accepted')
        elif filter_param == 'interested':
            jobs = jobs.filter(status='interested')
            
        if skill_name:
            jobs = jobs.filter(skills__name__icontains=skill_name)
            
        return jobs.prefetch_related('eigenbemuehungen', 'skills')

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
        context['active_filter'] = self.request.GET.get('filter', 'all')
        context['active_skill'] = self.request.GET.get('skill', '')
        context['skill_names'] = list(
            SkillTreeModel.objects.filter(
                jobs__user=self.request.user
            ).values_list('name', flat=True).distinct()[:50]
        )
        return context


class JobDashboardView(LoginRequiredMixin, TemplateView):
    """Unified Jobs + Nachweis dashboard."""
    template_name = 'jobs/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        start, end, label = _parse_period(self.request)
        profile = _get_profile(user)
        plan = _get_active_plan(user)
        all_in_range = Application.objects.filter(
            user=user,
            applied_on__gte=start,
            applied_on__lte=end,
        ).order_by("applied_on", "employer_name")
        nachweisbar = [a for a in all_in_range if a.is_nachweisbar]
        blockers = [a for a in all_in_range if not a.is_nachweisbar]
        target = plan.required_count if plan else None
        due_on = plan.next_due_on() if plan else None
        next_appointment = (
            Event.objects.filter(user=user, date__gte=timezone.now())
            .order_by("date")
            .first()
        )
        export_profile = _export_profile(self.request)
        open_vvs = Vermittlungsvorschlag.objects.filter(
            user=user, status=Vermittlungsvorschlag.Status.OPEN
        )
        unreported_absences = Absence.objects.filter(
            user=user, approval_status=Absence.ApprovalStatus.PENDING
        )
        recent_obstacles = Obstacle.objects.filter(user=user)[:10]
        last_submission = Submission.objects.filter(user=user).first()
        
        # Compliance timeline, newest first
        timeline_items = []
        for app in nachweisbar:
            timeline_items.append({
                'type': 'application',
                'title': f"{app.employer_name} — {app.job_title}",
                'subtitle': app.get_channel_display() or '',
                'date': app.applied_on,
                'badge': None,
                'badge_type': None,
                'edit_url': reverse('jobs:application_edit', kwargs={'pk': app.pk}),
            })
        for vv in open_vvs:
            timeline_items.append({
                'type': 'vv',
                'title': f"{vv.employer_name} — {vv.job_title or ''}",
                'subtitle': _("Placement proposal"),
                'date': vv.received_on,
                'badge': _("overdue") if vv.is_overdue else None,
                'badge_type': 'error' if vv.is_overdue else None,
                'edit_url': reverse('jobs:vv_edit', kwargs={'pk': vv.pk}),
            })
        for absence in unreported_absences:
            timeline_items.append({
                'type': 'absence',
                'title': _("Absence (Ortsabwesenheit)"),
                'subtitle': (
                    f"{absence.from_date:%d.%m.}–{absence.to_date:%d.%m.%Y}"
                    f" — {absence.destination or ''}"
                ),
                'date': absence.from_date,
                'badge': _("not reported"),
                'badge_type': 'error',
                'edit_url': reverse('jobs:absence_edit', kwargs={'pk': absence.pk}),
            })
        for o in recent_obstacles:
            timeline_items.append({
                'type': 'obstacle',
                'title': _("Obstacle (wichtiger Grund)"),
                'subtitle': f"{o.get_kind_display()} — {o.note or ''}",
                'date': o.date,
                'badge': None,
                'badge_type': None,
                'edit_url': reverse('jobs:obstacle_edit', kwargs={'pk': o.pk}),
            })
        timeline_items.sort(key=lambda item: item['date'], reverse=True)

        # Job postings with the same filters as the former job list
        active_filter = self.request.GET.get('filter', 'all')
        active_skill = self.request.GET.get('skill', '')
        jobs = JobPosting.objects.filter(user=user).order_by('-created_at')
        if active_filter == 'favorites':
            jobs = jobs.filter(favorites=user).distinct()
        elif active_filter == 'recent':
            jobs = jobs.order_by('-updated_at')[:10]
        elif active_filter == 'active':
            jobs = jobs.filter(status__in=['applied', 'interviewing'])
        elif active_filter == 'interviewing':
            jobs = jobs.filter(status='interviewing')
        elif active_filter == 'applied':
            jobs = jobs.filter(status='applied')
        elif active_filter == 'rejected':
            jobs = jobs.filter(status='rejected')
        elif active_filter == 'accepted':
            jobs = jobs.filter(status='accepted')
        elif active_filter == 'interested':
            jobs = jobs.filter(status='interested')
        if active_skill:
            jobs = jobs.filter(skills__name__icontains=active_skill)
        jobs = jobs.prefetch_related('eigenbemuehungen', 'skills')
        favorite_job_ids = list(
            user.favorited_jobs.values_list('id', flat=True)
        )
        skill_names = list(
            SkillTreeModel.objects.filter(jobs__user=user)
            .values_list('name', flat=True).distinct()[:50]
        )
        
        context.update({
            'profile': profile,
            'plan': plan,
            'plan_is_vague': plan.is_vague if plan else False,
            'plan_missing': plan.missing_components if plan else [],
            'period_label': label,
            'period_start': start,
            'period_end': end,
            'count': len(nachweisbar),
            'target': target,
            'progress_percent': (
                min(100, round(len(nachweisbar) / target * 100))
                if target else None
            ),
            'due_on': due_on,
            'days_until_due': (due_on - date.today()).days if due_on else None,
            'last_submitted_on': plan.last_submitted_on if plan else None,
            'last_submission': last_submission,
            'blockers': blockers,
            'export_profile': export_profile,
            'export_profiles': EXPORT_PROFILES,
            'current_month': date.today().strftime("%Y-%m"),
            'next_appointment': next_appointment,
            'open_vvs': open_vvs,
            'unreported_absences': unreported_absences,
            'recent_obstacles': recent_obstacles,
            'applications': nachweisbar,
            'timeline_items': timeline_items,
            'jobs': jobs,
            'favorite_job_ids': favorite_job_ids,
            'active_filter': active_filter,
            'active_skill': active_skill,
            'skill_names': skill_names,
            # expose Application result choices for inline select
            'application_result_choices': list(Application.Result.choices),
        })
        return context


class JobPostingDetailView(LoginRequiredMixin, DetailView):
    model = JobPosting
    template_name = 'jobs/detail.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).prefetch_related(
            'eigenbemuehungen', 'skills'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_favorite = context['job'].is_favorited_by(self.request.user)

        job_detail_component = JobDetailComponent()
        component_context = job_detail_component.get_context_data(
            job=context['job'],
            is_favorite=is_favorite
        )
        context.update(component_context)
        linked = list(context['job'].eigenbemuehungen.all())
        context['linked_applications'] = linked
        context['linked_count'] = sum(1 for a in linked if a.is_nachweisbar)
        return context


class JobCreateView(LoginRequiredMixin, CreateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/add.html'
    success_url = reverse_lazy('jobs:list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Job added successfully.'))

        if form.cleaned_data.get('record_effort'):
            effort_date = form.cleaned_data.get('effort_date') or date.today()
            channel_raw = form.cleaned_data.get('effort_channel')
            channel = int(channel_raw) if channel_raw and channel_raw.isdigit() else None
            Application.objects.create(
                user=self.request.user,
                job_posting=form.instance,
                employer_name=form.instance.company,
                job_title=form.instance.title,
                applied_on=effort_date,
                channel=channel,
                source=Application.Source.COMPANY_SITE,
                effort_type=Application.EffortType.BEWERBUNG,
            )
            messages.success(
                self.request,
                _('Effort recorded for %(date)s — linked to this job.') % {'date': effort_date},
            )

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
        messages.success(self.request, _('Job updated successfully.'))

        if form.cleaned_data.get('record_effort'):
            effort_date = form.cleaned_data.get('effort_date') or date.today()
            channel_raw = form.cleaned_data.get('effort_channel')
            channel = int(channel_raw) if channel_raw and channel_raw.isdigit() else None
            existing = Application.objects.filter(
                user=self.request.user,
                job_posting=form.instance,
                applied_on=effort_date,
            ).first()
            if not existing:
                Application.objects.create(
                    user=self.request.user,
                    job_posting=form.instance,
                    employer_name=form.instance.company,
                    job_title=form.instance.title,
                    applied_on=effort_date,
                    channel=channel,
                    source=Application.Source.COMPANY_SITE,
                    effort_type=Application.EffortType.BEWERBUNG,
                )
                messages.success(
                    self.request,
                    _('Effort recorded for %(date)s.') % {'date': effort_date},
                )
            else:
                messages.info(self.request, _('Effort for this date already exists.'))

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
        return JobPosting.objects.filter(favorites=self.request.user).distinct()


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        job = get_object_or_404(JobPosting, pk=pk, user=request.user)
        created = job.toggle_favorite(request.user)
        is_favorite = job.is_favorited_by(request.user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'is_favorite': is_favorite})
        if created:
            messages.success(request, 'Job added to favorites.')
        else:
            messages.success(request, 'Job removed from favorites.')
        return HttpResponseRedirect(
            request.META.get('HTTP_REFERER', reverse('jobs:list'))
        )


# ---------------------------------------------------------------------------
# Nachweis von Eigenbemühungen (Agentur für Arbeit / Jobcenter)
# ---------------------------------------------------------------------------

from .forms import (
    ApplicationForm,
    ObligationPlanForm,
    UserProfileForm,
    VermittlungsvorschlagForm,
    AbsenceForm,
    ObstacleForm,
)


class NachweisDashboardView(LoginRequiredMixin, ListView):
    """Calendar-month dashboard: count vs plan target, due date, blockers."""
    template_name = "jobs/nachweis/dashboard.html"
    context_object_name = "applications"

    def get_queryset(self):
        start, end, _label = _parse_period(self.request)
        return (
            Application.objects.filter(
                user=self.request.user,
                applied_on__gte=start,
                applied_on__lte=end,
            )
            .order_by("applied_on", "employer_name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        start, end, label = _parse_period(self.request)
        profile = _get_profile(user)
        plan = _get_active_plan(user)
        all_in_range = list(self.get_queryset())
        nachweisbar = [a for a in all_in_range if a.is_nachweisbar]
        blockers = [
            a for a in all_in_range
            if not a.is_nachweisbar
        ]
        target = plan.required_count if plan else None
        due_on = plan.next_due_on() if plan else None
        next_appointment = None
        try:
            from events.models import Event
            next_appointment = (
                Event.objects.filter(user=user, date__gte=timezone.now())
                .order_by("date")
                .first()
            )
        except Exception:
            pass
        export_profile = _export_profile(self.request)
        open_vvs = Vermittlungsvorschlag.objects.filter(
            user=user, status=Vermittlungsvorschlag.Status.OPEN
        )
        unreported_absences = Absence.objects.filter(
            user=user, approval_status=Absence.ApprovalStatus.PENDING
        )
        recent_obstacles = Obstacle.objects.filter(user=user)[:10]
        context.update(
            {
                "profile": profile,
                "plan": plan,
                "plan_is_vague": plan.is_vague if plan else False,
                "plan_missing": plan.missing_components if plan else [],
                "period_label": label,
                "period_start": start,
                "period_end": end,
                "count": len(nachweisbar),
                "target": target,
                "due_on": due_on,
                "days_until_due": (due_on - date.today()).days if due_on else None,
                "last_submitted_on": plan.last_submitted_on if plan else None,
                "last_submission": Submission.objects.filter(user=user).first(),
                "blockers": blockers,
                "export_profile": export_profile,
                "export_profiles": EXPORT_PROFILES,
                "current_month": date.today().strftime("%Y-%m"),
                "next_appointment": next_appointment,
                "open_vvs": open_vvs,
                "unreported_absences": unreported_absences,
                "recent_obstacles": recent_obstacles,
            }
        )
        return context


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = "jobs/nachweis/application_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = {"applied_on": date.today()}
        job_pk = self.request.GET.get("job_posting")
        if job_pk:
            job = JobPosting.objects.filter(pk=job_pk, user=self.request.user).first()
            if job:
                initial.update(
                    {
                        "employer_name": job.company,
                        "job_title": job.title,
                        "job_posting": job.pk,
                        "source": Application.Source.COMPANY_SITE,
                    }
                )
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _("Job search effort saved."))
        duplicate = Application.objects.filter(
            user=self.request.user,
            employer_name__iexact=form.cleaned_data["employer_name"],
            job_title__iexact=form.cleaned_data["job_title"],
            applied_on=form.cleaned_data["applied_on"],
        ).exclude(pk=self.object.pk)
        if duplicate.exists():
            messages.warning(
                self.request,
                _("Possible duplicate: an effort with the same employer, title and date already exists."),
            )
        return response

    def get_success_url(self):
        return reverse("jobs:list")


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = "jobs/nachweis/application_form.html"

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        changed_date = (
            "applied_on" in form.changed_data
        )
        response = super().form_valid(form)
        messages.success(self.request, _("Job search effort updated."))
        if changed_date:
            messages.warning(
                self.request,
                _("Only enter the real date of an effort that actually took place. This change has been recorded in the audit log."),
            )
        return response

    def get_success_url(self):
        return reverse("jobs:list")


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = "jobs/nachweis/application_delete.html"

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("jobs:list")


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = "jobs/nachweis/application_detail.html"
    context_object_name = "application"

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class EvidenceCreateView(LoginRequiredMixin, CreateView):
    model = EvidenceFile
    fields = ["file", "evidence_type"]
    template_name = "jobs/nachweis/evidence_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application"] = get_object_or_404(
            Application, pk=self.kwargs["pk"], user=self.request.user
        )
        return context

    def form_valid(self, form):
        application = get_object_or_404(
            Application, pk=self.kwargs["pk"], user=self.request.user
        )
        form.instance.user = self.request.user
        form.instance.application = application
        messages.success(self.request, _("Evidence file saved."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:application_detail", kwargs={"pk": self.kwargs["pk"]})


class ObligationPlanEditView(LoginRequiredMixin, UpdateView):
    model = ObligationPlan
    form_class = ObligationPlanForm
    template_name = "jobs/nachweis/plan_form.html"

    def get_object(self, queryset=None):
        return _get_active_plan(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_new"] = self.object is None
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _("Obligation plan saved."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:list")


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "jobs/nachweis/profile_form.html"

    def get_object(self, queryset=None):
        return _get_profile(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _("Profile saved."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:list")


@login_required
def plan_drawer(request):
    user = request.user
    plan = _get_active_plan(user)
    if request.method == 'POST':
        form = ObligationPlanForm(request.POST, instance=plan)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.user = user
            inst.save()
            # Return a small success fragment for HTMX and signal the client to close the drawer
            return HttpResponse('<div class="p-4"><div class="text-sm text-success">' + _('Obligation plan saved.') + '</div><script>window.dispatchEvent(new Event("close-drawer"));</script></div>')
        else:
            return render(request, 'jobs/partials/plan_drawer.html', {'form': form})
    form = ObligationPlanForm(instance=plan)
    return render(request, 'jobs/partials/plan_drawer.html', {'form': form})


@login_required
def profile_drawer(request):
    user = request.user
    profile = _get_profile(user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.user = user
            inst.save()
            # Return a small success fragment for HTMX and signal the client to close the drawer
            return HttpResponse('<div class="p-4"><div class="text-sm text-success">' + _('Profile saved.') + '</div><script>window.dispatchEvent(new Event("close-drawer"));</script></div>')
        else:
            return render(request, 'jobs/partials/profile_drawer.html', {'form': form})
    form = UserProfileForm(instance=profile)
    return render(request, 'jobs/partials/profile_drawer.html', {'form': form})


@login_required
def application_drawer(request):
    """Render or process the quick-add/edit drawer for Applications.
    Accepts optional GET/POST 'pk' for editing an existing Application.
    """
    pk = request.GET.get('pk') or request.POST.get('pk')
    instance = None
    if pk:
        instance = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=instance, user=request.user)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.save()
            # warn if date changed (maintain existing UX)
            if 'applied_on' in form.changed_data:
                msg = _('Job search effort updated.')
            else:
                msg = _('Job search effort saved.')
            # Return a small success fragment for HTMX and signal the client to close the drawer
            return HttpResponse('<div class="p-4"><div class="text-sm text-success">' + msg + '</div><script>window.dispatchEvent(new Event("close-drawer"));</script></div>')
        else:
            return render(request, 'jobs/partials/application_drawer.html', {'form': form})
    form = ApplicationForm(instance=instance, user=request.user)
    return render(request, 'jobs/partials/application_drawer.html', {'form': form})


@login_required
def application_inline_update(request, pk):
    """JSON endpoint for inline edits (date/status) on Application rows.
    Performs a minimal, safe partial update on allowed fields and preserves
    Application.save() (and its AuditLog behaviour) by updating the instance
    and calling full_clean()/save().
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    app = get_object_or_404(Application, pk=pk, user=request.user)
    # Accept JSON or form-encoded
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        data = request.POST.dict()
    # Allowed fields for inline update
    allowed = {'applied_on', 'result', 'result_date'}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return JsonResponse({'error': 'No updatable field provided'}, status=400)
    # Parse and apply values
    from django.core.exceptions import ValidationError
    from django.utils.dateparse import parse_date
    try:
        if 'applied_on' in updates:
            parsed = parse_date(updates['applied_on'])
            if not parsed:
                raise ValidationError({'applied_on': ['Invalid date format']})
            app.applied_on = parsed
        if 'result_date' in updates:
            parsed = parse_date(updates['result_date'])
            if not parsed:
                raise ValidationError({'result_date': ['Invalid date format']})
            app.result_date = parsed
        if 'result' in updates:
            app.result = updates['result']
        # Validate model instance (will use existing field values for required fields)
        app.full_clean()
        app.save()
        # Prepare response with updated values
        resp = {}
        for f in updates:
            val = getattr(app, f)
            if hasattr(val, 'isoformat'):
                resp[f] = val.isoformat()
            else:
                resp[f] = val
        return JsonResponse({'success': True, 'updated': resp})
    except ValidationError as e:
        # Return field errors
        return JsonResponse({'success': False, 'errors': e.message_dict}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


class NachweisExportView(LoginRequiredMixin, TemplateView):
    """Export chooser page: profile + period, links to PDF/CSV/JSON."""
    template_name = "jobs/nachweis/export.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start, end, label = _parse_period(self.request)
        context.update(
            {
                "export_profiles": EXPORT_PROFILES,
                "period_label": label,
                "period_start": start,
                "period_end": end,
                "count": _nachweisbar_qs(
                    self.request.user, start, end
                ).count(),
                "current_month": date.today().strftime("%Y-%m"),
            }
        )
        return context


class NachweisExportBaseView(LoginRequiredMixin, View):
    """Shared period/profile handling for the download endpoints."""

    export_profile = nachweis_pdf.JOBCENTER_LIST

    def _context(self, request):
        start, end, label = _parse_period(request)
        user = request.user
        return {
            "user": user,
            "start": start,
            "end": end,
            "label": label,
            "profile": _get_profile(user),
            "plan": _get_active_plan(user),
            "export_profile": _export_profile(request),
            "applications": _nachweisbar_qs(user, start, end),
        }

    def _record_submission(self, ctx, profile_code):
        Submission.objects.create(
            user=ctx["user"],
            plan=ctx["plan"],
            profile=profile_code,
            period_from=ctx["start"],
            period_to=ctx["end"],
            rows=ctx["applications"].count(),
        )
        if ctx["plan"]:
            ObligationPlan.objects.filter(pk=ctx["plan"].pk).update(
                last_submitted_on=date.today()
            )

    def _empty_response(self):
        messages.error(
            self.request,
            _("No exportable applications in the selected period — nothing was generated."),
        )
        return HttpResponseRedirect(reverse("jobs:nachweis_export"))


class NachweisPDFView(NachweisExportBaseView):
    def get(self, request):
        ctx = self._context(request)
        try:
            pdf_bytes = nachweis_pdf.build_nachweis_pdf(
                person=ctx["profile"],
                plan=ctx["plan"],
                applications=ctx["applications"],
                export_profile=ctx["export_profile"],
            )
        except nachweis_pdf.EmptyNachweisError:
            return self._empty_response()
        self._record_submission(ctx, ctx["export_profile"])
        year, month = ctx["start"].year, ctx["start"].month
        filename = nachweis_pdf.nachweis_filename(ctx["profile"], year, month)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class NachweisPreviewView(NachweisExportBaseView):
    """In-browser WYSIWYG preview of the exact PDF layout."""

    def get(self, request):
        ctx = self._context(request)
        try:
            html_doc = nachweis_pdf.build_nachweis_html(
                person=ctx["profile"],
                plan=ctx["plan"],
                applications=ctx["applications"],
                export_profile=ctx["export_profile"],
            )
        except nachweis_pdf.EmptyNachweisError:
            return self._empty_response()
        return HttpResponse(html_doc, content_type="text/html; charset=utf-8")


class NachweisCSVView(NachweisExportBaseView):
    def get(self, request):
        ctx = self._context(request)
        csv_text = nachweis_exports.build_csv(ctx["applications"])
        if not ctx["applications"].exists():
            return self._empty_response()
        self._record_submission(ctx, "CSV")
        response = HttpResponse(csv_text, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="Nachweis_Eigenbemuehungen_{ctx["start"]:%Y-%m}.csv"'
        )
        return response


class NachweisJSONView(NachweisExportBaseView):
    def get(self, request):
        ctx = self._context(request)
        json_text = nachweis_exports.build_json(
            ctx["profile"], ctx["plan"], ctx["applications"]
        )
        response = HttpResponse(json_text, content_type="application/json")
        response["Content-Disposition"] = (
            f'attachment; filename="Nachweis_Eigenbemuehungen_{ctx["start"]:%Y-%m}.json"'
        )
        return response


# --- Vermittlungsvorschlag CRUD ---

class VermittlungsvorschlagCreateView(LoginRequiredMixin, CreateView):
    model = Vermittlungsvorschlag
    form_class = VermittlungsvorschlagForm
    template_name = "jobs/nachweis/vv_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        return {"received_on": date.today()}

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _("Vermittlungsvorschlag saved."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:list")


class VermittlungsvorschlagUpdateView(LoginRequiredMixin, UpdateView):
    model = Vermittlungsvorschlag
    form_class = VermittlungsvorschlagForm
    template_name = "jobs/nachweis/vv_form.html"

    def get_queryset(self):
        return Vermittlungsvorschlag.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Vermittlungsvorschlag updated."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:list")


class VermittlungsvorschlagDeleteView(LoginRequiredMixin, DeleteView):
    model = Vermittlungsvorschlag
    template_name = "jobs/nachweis/vv_delete.html"

    def get_queryset(self):
        return Vermittlungsvorschlag.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("jobs:list")


class VermittlungsvorschlagListView(LoginRequiredMixin, ListView):
    model = Vermittlungsvorschlag
    template_name = "jobs/nachweis/vv_list.html"
    context_object_name = "vvs"

    def get_queryset(self):
        return Vermittlungsvorschlag.objects.filter(user=self.request.user)


# --- Absence CRUD ---

class AbsenceCreateView(LoginRequiredMixin, CreateView):
    model = Absence
    form_class = AbsenceForm
    template_name = "jobs/nachweis/absence_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _("Absence saved."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:list")


class AbsenceUpdateView(LoginRequiredMixin, UpdateView):
    model = Absence
    form_class = AbsenceForm
    template_name = "jobs/nachweis/absence_form.html"

    def get_queryset(self):
        return Absence.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _("Absence updated."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:list")


class AbsenceDeleteView(LoginRequiredMixin, DeleteView):
    model = Absence
    template_name = "jobs/nachweis/absence_delete.html"

    def get_queryset(self):
        return Absence.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("jobs:list")


# --- Obstacle (wichtiger Grund) CRUD ---

class ObstacleCreateView(LoginRequiredMixin, CreateView):
    model = Obstacle
    form_class = ObstacleForm
    template_name = "jobs/nachweis/obstacle_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _("Obstacle logged."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:list")


class ObstacleUpdateView(LoginRequiredMixin, UpdateView):
    model = Obstacle
    form_class = ObstacleForm
    template_name = "jobs/nachweis/obstacle_form.html"

    def get_queryset(self):
        return Obstacle.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("Obstacle updated."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("jobs:list")


class ObstacleDeleteView(LoginRequiredMixin, DeleteView):
    model = Obstacle
    template_name = "jobs/nachweis/obstacle_delete.html"

    def get_queryset(self):
        return Obstacle.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("jobs:list")


# --- ZIP + Kostenbeleg exports ---

class NachweisZIPView(NachweisExportBaseView):
    def get(self, request):
        ctx = self._context(request)
        apps = list(ctx["applications"])
        if not apps:
            return self._empty_response()
        try:
            pdf_bytes = nachweis_pdf.build_nachweis_pdf(
                person=ctx["profile"],
                plan=ctx["plan"],
                applications=apps,
                export_profile=nachweis_pdf.JOBCENTER_LIST,
            )
        except nachweis_pdf.EmptyNachweisError:
            return self._empty_response()
        evidence_mapping = {}
        for app in apps:
            attachments = app.attachments.all()
            if attachments:
                evidence_mapping[app] = list(attachments)
        year, month = ctx["start"].year, ctx["start"].month
        pdf_name = nachweis_pdf.nachweis_filename(ctx["profile"], year, month)
        zip_bytes = nachweis_exports.build_zip(
            pdf_bytes, pdf_name, apps, evidence_mapping
        )
        response = HttpResponse(zip_bytes, content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="Nachweis_Eigenbemuehungen_{year:04d}-{month:02d}.zip"'
        )
        return response
