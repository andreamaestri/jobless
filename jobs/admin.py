from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import JobPosting, SkillTreeModel, JobSkill


class SkillTreeModelAdmin(ModelAdmin):
    list_display = ('name', 'label', 'path', 'icon')
    search_fields = ('name', 'label')
    list_filter = ('icon',)
    fields = ('name', 'icon', 'description')
    ordering = ('name',)


@admin.register(SkillTreeModel)
class SkillTreeModelAdmin(SkillTreeModelAdmin):
    pass


@admin.register(JobSkill)
class JobSkillAdmin(ModelAdmin):
    list_display = [
        'job',
        'skill',
        'proficiency'
    ]
    search_fields = [
        'job__title',
        'skill__name'
    ]
    list_filter = ['proficiency']


class JobSkillInline(TabularInline):  # Change to Unfold's TabularInline
    model = JobSkill
    extra = 1


@admin.register(JobPosting)
class JobPostingAdmin(ModelAdmin):
    # Display fields in list view
    list_display = [
        'title',
        'company',
        'location',
        'status',
        'created_at',
        'updated_at'
    ]
    
    # Fields to search
    search_fields = ['title', 'company', 'description']
    
    # Filters in the right sidebar
    list_filter = ['status', 'created_at', 'company']
    
    # Readonly fields
    readonly_fields = ['created_at', 'updated_at']
    
    # Fields to show in the edit form
    fields = [
        'title',
        'company',
        'location',
        'salary_range',
        'url',
        'description',
        'status',
        'user',
        'created_at',
        'updated_at'
    ]
    
    inlines = [JobSkillInline]
    
    # Enable features
    list_filter_submit = True  # Add submit button in filters
    warn_unsaved_form = True   # Warn before leaving unsaved changes
    list_fullwidth = True      # Use full width for list view
    
    # Preprocess content of readonly fields
    readonly_preprocess_fields = {
        "description": lambda content: content.strip(),
    }
    
    # Custom list actions
    actions = [
        'mark_as_applied',
        'mark_as_interviewing',
        'mark_as_rejected'
    ]
    
    def mark_as_applied(self, request, queryset):
        queryset.update(status='applied')
    mark_as_applied.short_description = (
        "Mark selected jobs as Applied"
    )
    
    def mark_as_interviewing(self, request, queryset):
        queryset.update(status='interviewing')
    mark_as_interviewing.short_description = (
        "Mark selected jobs as Interviewing"
    )
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = (
        "Mark selected jobs as Rejected"
    )
