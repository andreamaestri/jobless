from django.urls import path
from .views import (
    JobListView, JobCreateView, JobPostingUpdateView,
    JobPostingDeleteView, JobPostingDetailView, JobFavoritesListView,
    toggle_favourite, skills_autocomplete, get_skills_data,
    parse_job_description
)

app_name = 'jobs'

urlpatterns = [
    path('', JobListView.as_view(), name='list'),
    path('add/', JobCreateView.as_view(), name='add'),
    path('edit/<int:pk>/', JobPostingUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', JobPostingDeleteView.as_view(), name='delete'),
    path('detail/<int:pk>/', JobPostingDetailView.as_view(), name='detail'),
    path('favourites/', JobFavoritesListView.as_view(), name='favourites'),
    path('toggle-favourite/<int:job_id>/', toggle_favourite, name='toggle_favourite'),
    path('skills/autocomplete/', skills_autocomplete, name='skills_autocomplete'),
    path('skills/data/', get_skills_data, name='skills_data'),
    path('parse-description/', parse_job_description, name='parse_description'),
]