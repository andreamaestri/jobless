from django.shortcuts import get_object_or_404
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
)
from django.views.generic.edit import FormMixin
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
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

from datetime import date, timedelta
from django.http import HttpResponse
from django.utils.translation import gettext as _

from .models import (
    JobPosting,
    UserProfile,
    ObligationPlan,
    Application,
    EvidenceFile,
    Submission,
    Vermittlungsvorschlag,
    Absence,
    Obstacle,
)
from .forms import (
    ApplicationForm,
    ObligationPlanForm,
    UserProfileForm,
    VermittlungsvorschlagForm,
    AbsenceForm,
    ObstacleForm,
)
from . import pdf as nachweis_pdf
from . import exports as nachweis_exports

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
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = "jobs/nachweis/application_delete.html"

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


class VermittlungsvorschlagDeleteView(LoginRequiredMixin, DeleteView):
    model = Vermittlungsvorschlag
    template_name = "jobs/nachweis/vv_delete.html"

    def get_queryset(self):
        return Vermittlungsvorschlag.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


class AbsenceDeleteView(LoginRequiredMixin, DeleteView):
    model = Absence
    template_name = "jobs/nachweis/absence_delete.html"

    def get_queryset(self):
        return Absence.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


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
        return reverse("jobs:nachweis")


class ObstacleDeleteView(LoginRequiredMixin, DeleteView):
    model = Obstacle
    template_name = "jobs/nachweis/obstacle_delete.html"

    def get_queryset(self):
        return Obstacle.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("jobs:nachweis")


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
