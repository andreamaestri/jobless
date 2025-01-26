from django.urls import path
import tagulous.views
from . import views
from .models import SkillTag

app_name = 'jobs'

urlpatterns = [
    path('api/skills/', views.api_skills, name='api_skills'),
    path('', views.JobListView.as_view(), name='list'),
    path('add/', views.JobCreateView.as_view(), name='add'),
    path('<int:pk>/', views.JobPostingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.JobPostingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='delete'),
    path('skills/autocomplete/', views.skills_autocomplete, name='skills_autocomplete'),
    path('parse-description/', views.parse_job_description, name='parse_description'),
    path('favorites/', views.JobFavoritesView.as_view(), name='favorites'),
    path('job/<int:pk>/toggle-favorite/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path(
        'skill-tags-autocomplete/',
        tagulous.views.autocomplete,
        {'tag_model': SkillTag},
        name='skill_tags_autocomplete'  # Matches the TagMeta autocomplete_view
    ),
]
