from django.urls import path
from . import views


app_name = 'jobs'

urlpatterns = [
    path('', views.JobPostingListView.as_view(), name='list'),
    path('add/', views.JobPostingCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.JobPostingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='delete'),
    path('<int:pk>/', views.JobPostingDetailView.as_view(), name='detail'),
    path('toggle-favourite/<int:job_id>/', views.toggle_favourite, name='toggle_favourite'),
    path('favourites/', views.favourited_jobs, name='favourites'),
]
