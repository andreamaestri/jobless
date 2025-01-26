from django.urls import path
from . import views
from .models import SkillTreeModel
import tagulous.views

urlpatterns = [
    path('', views.JobListView.as_view(), name='list'),
    path('add/', views.JobCreateView.as_view(), name='add'),
    path('<int:pk>/', views.JobPostingDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.JobPostingUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='delete'),
    path('favorites/', views.JobFavoritesView.as_view(), name='favorites'),
    path('<int:pk>/toggle-favorite/', 
         views.ToggleFavoriteView.as_view(), 
         name='toggle-favorite'),
    
    # API endpoints     
    path('skills/', views.api_skills, name='api_skills'),
    path('skills/autocomplete/', views.skills_autocomplete, name='skills_autocomplete'),
    path('parse-description/', views.parse_job_description, name='parse_description'),
         
    # Tag autocomplete
    path('skill-tags/autocomplete/',
         tagulous.views.autocomplete,
         {'tag_model': SkillTreeModel},
         name='skill_tags_autocomplete'),
]
