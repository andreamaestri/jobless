from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.JobListView.as_view(), name='list'),
    path('add/', views.JobCreateView.as_view(), name='add'),
    path('<int:pk>/', views.JobPostingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.JobPostingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='delete'),
    path('<int:pk>/toggle-favorite/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('favorites/', views.JobFavoritesListView.as_view(), name='favorites'),
    path('skills/autocomplete/', views.skills_autocomplete, name='skills_autocomplete'),
    path('skills/list/', views.skills_autocomplete, {'all': True}, name='skills_list'),
    path('parse-description/', views.parse_job_description, name='parse_description'),
]
