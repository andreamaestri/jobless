from django.urls import path
from . import views


app_name = 'jobs'

urlpatterns = [
    path('', views.FoodListView.as_view(), name='list'),
    path('add/', views.FoodCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.FoodUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.FoodDeleteView.as_view(), name='delete'),
    path('toggle_favourite/<int:job_id>/', views.favourited_jobs,
            name='toggle_favourite'),
    path('favourited_jobs/', views.favourited_jobs, name='favourites.html'),
]
