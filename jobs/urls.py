from django.urls import path
import django_tagulous.views
from . import views
from .models import SkillTag

app_name = 'jobs'

urlpatterns = [
    path('api/skills/', views.api_skills, name='api_skills'),
    path('', views.JobListView.as_view(), name='list'),
    path('add/', views.JobCreateView.as_view(), name='add'),
    path('<int:pk>/', views.JobPostingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.JobPostingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='delete'),
    path('skills/autocomplete/', views.skills_autocomplete, name='skills_autocomplete'),
    path('parse-description/', views.parse_job_description, name='parse_description'),
    path('favorites/', views.JobFavoritesView.as_view(), name='favorites'),
    path('job/<int:pk>/toggle-favorite/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path(
        'skill-tags-autocomplete/',
        django_tagulous.views.autocomplete,
        {'tag_model': SkillTag},
        name='skill_tags_autocomplete'  # Matches the TagMeta autocomplete_view
    ),
    # Nachweis von Eigenbemühungen
    path('nachweis/', views.NachweisDashboardView.as_view(), name='nachweis'),
    path('nachweis/add/', views.ApplicationCreateView.as_view(), name='application_add'),
    path('nachweis/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('nachweis/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_edit'),
    path('nachweis/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),
    path('nachweis/<int:pk>/evidence/add/', views.EvidenceCreateView.as_view(), name='evidence_add'),
    path('nachweis/plan/', views.ObligationPlanEditView.as_view(), name='plan_edit'),
    path('nachweis/profile/', views.UserProfileEditView.as_view(), name='profile_edit'),
    path('nachweis/export/', views.NachweisExportView.as_view(), name='nachweis_export'),
    path('nachweis/export/pdf/', views.NachweisPDFView.as_view(), name='nachweis_pdf'),
    path('nachweis/export/preview/', views.NachweisPreviewView.as_view(), name='nachweis_preview'),
    path('nachweis/export/csv/', views.NachweisCSVView.as_view(), name='nachweis_csv'),
    path('nachweis/export/json/', views.NachweisJSONView.as_view(), name='nachweis_json'),
]
