from django.urls import path
from .views import HomeView, api_search


app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/search/', api_search, name='api_search'),
]
