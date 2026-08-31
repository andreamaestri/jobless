from django.urls import path

from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.assistant_home, name='assistant'),
    path('cv/save/', views.save_cv, name='save_cv'),
    path('generate/', views.generate, name='generate'),
    path('runs/fragment/', views.runs_fragment, name='runs_fragment'),
    path('runs/<int:pk>/delete/', views.delete_run, name='delete_run'),
]
