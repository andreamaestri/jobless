from django.urls import path
from . import views
import tagulous.views
from .models import SkillsTagModel

app_name = 'jobs'

urlpatterns = [
    # List and CRUD operations
    path('', views.JobPostingListView.as_view(), name='list'),
    path('add/', views.JobPostingCreateView.as_view(), name='add'),
    path('<int:pk>/', views.JobPostingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.JobPostingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='delete'),
    
    # Favorites functionality
    path('favourites/', views.favourited_jobs, name='favourites'),
    path('toggle-favourite/<int:job_id>/', views.toggle_favourite, name='toggle_favourite'),
    
    # Skills API endpoints
    path('api/skills/', views.get_skills_data, name='skills_data'),
    path('skills-autocomplete/', views.skills_autocomplete, name='skills_autocomplete'),
]