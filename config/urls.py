"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
<<<<<<< HEAD
    path("__reload__/", include("django_browser_reload.urls")),
=======
>>>>>>> 336107e031fd801cd8e364b15cd823a0d8b89e2a
    path("accounts/", include("allauth.urls")),
    path('admin/', admin.site.urls),
    path('ai-assistant/', include('ai_assistant.urls', namespace='ai_assistant')),
    path('contacts/', include('contacts.urls')),
    path('events/', include('events.urls')),
    path('jobs/', include('jobs.urls')),
<<<<<<< HEAD
=======
    path('events/', include('events.urls')),
>>>>>>> 336107e031fd801cd8e364b15cd823a0d8b89e2a
    path('', include ('home.urls')),
    
]
