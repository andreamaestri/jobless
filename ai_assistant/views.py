import json
import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Value, When
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime
from django.views.decorators.http import require_POST

from jobs.models import JobPosting

from .models import AssistantRun, UserCV
from . import services

logger = logging.getLogger(__name__)

STATUS_ORDER = ['interviewing', 'applied', 'interested', 'rejected', 'accepted']

GENERATION_ERROR = "The AI assistant is temporarily unavailable. Please try again later."


def _sse(payload):
    return f"data: {json.dumps(payload)}\n\n"


def _user_jobs(user):
    whens = [
        When(status=status, then=Value(priority))
        for priority, status in enumerate(STATUS_ORDER)
    ]
    return (
        JobPosting.objects.filter(user=user)
        .annotate(_priority=Case(*whens, default=len(STATUS_ORDER), output_field=IntegerField()))
        .order_by('_priority', '-updated_at')
    )


def _jobs_payload(jobs):
    return [
        {
            'id': job.pk,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'status': job.status,
        }
        for job in jobs
    ]


@login_required
def assistant_home(request):
    cv = UserCV.objects.filter(user=request.user).first()
    jobs = _user_jobs(request.user)
    initial_job_id = request.GET.get('job')
    valid_ids = set(jobs.values_list('id', flat=True))
    if not initial_job_id or int(initial_job_id) not in valid_ids:
        initial_job_id = jobs.first().pk if jobs.exists() else ''
    return render(
        request,
        'ai_assistant/assistant.html',
        {
            'cv': cv,
            'jobs': jobs,
            'jobs_json': _jobs_payload(jobs),
            'initial_job_id': initial_job_id,
            'has_cv': bool(cv and cv.content.strip()),
            'recent_runs': _recent_runs(request.user),
        },
    )


def _recent_runs(user):
    return (
        AssistantRun.objects.filter(user=user)
        .select_related('job')
        .prefetch_related('job__job_skills')[:8]
    )


@login_required
@require_POST
def save_cv(request):
    content = (request.POST.get('content') or '').strip()
    if not content:
        return JsonResponse({'ok': False, 'error': 'CV content cannot be empty.'}, status=400)
    if len(content) > services.CV_MAX_CHARS:
        return JsonResponse(
            {'ok': False, 'error': f'CV is too long ({len(content)} chars, max {services.CV_MAX_CHARS}).'},
            status=400,
        )
    cv, _ = UserCV.objects.update_or_create(user=request.user, defaults={'content': content})
    return JsonResponse({
        'ok': True,
        'updated_at': localtime(cv.updated_at).strftime('%d %b %Y, %H:%M'),
    })


@login_required
@require_POST
def generate(request):
    kind = request.POST.get('kind')
    if kind not in ('feedback', 'cover_letter'):
        return JsonResponse({'ok': False, 'error': 'Unknown tool.'}, status=400)

    cv = UserCV.objects.filter(user=request.user).first()
    if cv is None or not cv.content.strip():
        return JsonResponse({'ok': False, 'error': 'Save your CV first.'}, status=400)

    job = None
    job_id = request.POST.get('job')
    if job_id:
        job = get_object_or_404(JobPosting, pk=job_id, user=request.user)
    if kind == 'cover_letter' and job is None:
        return JsonResponse({'ok': False, 'error': 'Pick a job to write a cover letter for.'}, status=400)

    extra = services.clean_extra_instructions(request.POST.get('extra'))
    tone = request.POST.get('tone', 'professional')

    if kind == 'feedback':
        messages = services.feedback_messages(cv.content, job, extra)
        task = 'feedback'
    else:
        messages = services.cover_letter_messages(
            cv.content, job, tone=tone, extra_instructions=extra,
            candidate_name=request.user.get_full_name() or request.user.get_username(),
        )
        task = 'cover_letter'

    def event_stream():
        chunks = []
        try:
            for delta in services.stream_completion(messages, task=task):
                chunks.append(delta)
                yield _sse({'type': 'delta', 'text': delta})
            run = _create_run(request.user, kind, job, ''.join(chunks))
            yield _sse({'type': 'done', 'run_id': run.pk})
        except Exception:
            logger.exception("AI generation failed kind=%s", kind)
            if chunks:
                _create_run(request.user, kind, job, ''.join(chunks))
                yield _sse({'type': 'partial_saved'})
            yield _sse({'type': 'error', 'message': GENERATION_ERROR})

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def _create_run(user, kind, job, output):
    return AssistantRun.objects.create(user=user, kind=kind, job=job, output=output)


@login_required
def runs_fragment(request):
    return render(
        request,
        'ai_assistant/_history.html',
        {'recent_runs': _recent_runs(request.user)},
    )


@login_required
@require_POST
def delete_run(request, pk):
    run = get_object_or_404(AssistantRun, pk=pk, user=request.user)
    run.delete()
    return JsonResponse({'ok': True})
