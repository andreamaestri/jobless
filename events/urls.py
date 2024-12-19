from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='list'),
    path('add/', views.EventCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.EventUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.EventDeleteView.as_view(), name='delete'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='detail'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/events/', views.calendar_events, name='calendar_events'),
]