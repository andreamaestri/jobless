from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import JobPosting, SkillsTagModel

class SkillsTagModelAdmin(ModelAdmin):
    list_display = ('name', 'icon', 'icon_dark')
    search_fields = ('name',)
    list_filter = ('icon',)
    fields = ('name', 'icon', 'icon_dark')
    ordering = ('name',)

@admin.register(SkillsTagModel)
class SkillsTagModelAdmin(SkillsTagModelAdmin):
    pass

@admin.register(JobPosting)
class JobPostingAdmin(ModelAdmin):
    # Display fields in list view
    list_display = ['title', 'company', 'location', 'status', 'created_at', 'updated_at']
    
    # Fields to search
    search_fields = ['title', 'company', 'description', 'skills']
    
    # Filters in the right sidebar
    list_filter = ['status', 'created_at', 'company']
    
    # Readonly fields
    readonly_fields = ['created_at', 'updated_at']
    
    # Fields to show in the edit form
    fields = ['title', 'company', 'location', 'salary_range', 'url', 
             'description', 'skills', 'status', 'user', 'favorite',
             'created_at', 'updated_at']
    
    # Enable features
    list_filter_submit = True  # Add submit button in filters
    warn_unsaved_form = True   # Warn before leaving unsaved changes
    list_fullwidth = True      # Use full width for list view
    
    # Preprocess content of readonly fields
    readonly_preprocess_fields = {
        "description": lambda content: content.strip(),
    }
    
    # Custom list actions
    actions = ['mark_as_applied', 'mark_as_interviewing', 'mark_as_rejected']
    
    def mark_as_applied(self, request, queryset):
        queryset.update(status='applied')
    mark_as_applied.short_description = "Mark selected jobs as Applied"
    
    def mark_as_interviewing(self, request, queryset):
        queryset.update(status='interviewing')
    mark_as_interviewing.short_description = "Mark selected jobs as Interviewing"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = "Mark selected jobs as Rejected"
