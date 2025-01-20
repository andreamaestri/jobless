from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.JobListView.as_view(), name='list'),
    path('add/', views.JobCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.JobPostingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='delete'),
    path('<int:pk>/', views.JobPostingDetailView.as_view(), name='detail'),
    path('favourites/', views.JobFavoritesListView.as_view(), name='favourites'),
    path('<int:job_id>/toggle_favorite/', views.toggle_favourite, name='toggle_favorite'),
    path('toggle-favourite/<int:job_id>/', views.toggle_favourite, name='toggle_favourite'),
    path('skills/autocomplete/', views.skills_autocomplete, name='skills_autocomplete'),
    path('skills/list/', views.skills_autocomplete, {'all': True}, name='skills_list'),  # Add this new route
    path('parse-description/', views.parse_job_description, name='parse_description'),  # Keep the URL path the same but ensure view exists
]
