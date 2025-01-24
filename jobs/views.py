from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Job
from .forms import JobForm
from .components.job_list_component import JobListComponent
from .components.job_detail_component import JobDetailComponent
from .components.job_form_component import JobFormComponent

@login_required
def job_list(request):
    # Existing filtering logic
    filter_param = request.GET.get('filter', 'all')
    
    # Base queryset
    jobs = Job.objects.filter(user=request.user).order_by('-created_at')
    
    # Apply filters
    if filter_param == 'favorites':
        jobs = jobs.filter(favorited_by=request.user)
    elif filter_param == 'recent':
        jobs = jobs.order_by('-updated_at')[:10]
    elif filter_param == 'active':
        jobs = jobs.filter(status__in=['APPLIED', 'INTERVIEWING'])
    elif filter_param == 'interviewing':
        jobs = jobs.filter(status='INTERVIEWING')
    
    # Get favorite job IDs
    favorite_job_ids = list(request.user.favorite_jobs.values_list('id', flat=True))
    
    # Use the JobListComponent
    job_list_component = JobListComponent()
    context = job_list_component.get_context_data(
        jobs=jobs, 
        favorite_job_ids=favorite_job_ids
    )
    
    return render(request, 'jobs/list.html', context)

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, user=request.user)
    
    # Check if the job is a favorite
    is_favorite = request.user in job.favorited_by.all()
    
    # Use the JobDetailComponent
    job_detail_component = JobDetailComponent()
    context = job_detail_component.get_context_data(
        job=job,
        is_favorite=is_favorite
    )
    
    return render(request, 'jobs/detail.html', context)

@login_required
def job_add(request):
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Job added successfully.')
            return redirect('jobs:list')
    else:
        form = JobForm()
    
    # Use the JobFormComponent
    job_form_component = JobFormComponent()
    context = job_form_component.get_context_data(form=form)
    
    return render(request, 'jobs/add.html', context)

@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            job = form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    
    # Use the JobFormComponent
    job_form_component = JobFormComponent()
    context = job_form_component.get_context_data(
        form=form, 
        job=job
    )
    
    return render(request, 'jobs/edit.html', context)
