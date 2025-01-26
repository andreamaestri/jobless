from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from .models import JobPosting, SkillTreeModel, JobSkill


@admin.register(SkillTreeModel)
class SkillTreeModelAdmin(ModelAdmin):
    list_display = ('name', 'label', 'path', 'display_icon')
    search_fields = ['name', 'label']  # Enable search for autocomplete
    list_filter = ('icon',)
    fields = ('name', 'icon', 'description')
    ordering = ('name',)
    verbose_name = "Skill Catalog"
    verbose_name_plural = "Skill Catalog"

    class Media:
        extend = True
        js = ['https://code.iconify.design/iconify-icon/2.3.0/iconify-icon.min.js']

    def display_icon(self, obj):
        if obj.icon:
            return format_html(
                '<div style="display: flex; align-items: center; gap: 8px;">'
                '<iconify-icon icon="{}" width="20" height="20"></iconify-icon>'
                '<span>{}</span>'
                '</div>',
                obj.icon,
                obj.icon
            )
        return '-'
    display_icon.short_description = 'Icon'


@admin.register(JobSkill)
class JobSkillAdmin(ModelAdmin):
    verbose_name = "Job Skill Assignment"
    verbose_name_plural = "Job Skill Assignments"
    list_display = [
        'job',
        'skill_with_icon',
        'proficiency'
    ]
    search_fields = [
        'job__title',
        'skill__name'
    ]
    list_filter = ['proficiency']

    def skill_with_icon(self, obj):
        icon = obj.skill.icon if obj.skill and obj.skill.icon else 'heroicons:academic-cap'
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<iconify-icon icon="{}" width="20" height="20"></iconify-icon>'
            '<span>{}</span>'
            '</div>',
            icon,
            obj.skill.name
        )
    skill_with_icon.short_description = 'Skill'


class JobSkillInline(TabularInline):
    model = JobSkill
    extra = 1
    fields = ('skill', 'proficiency')
    autocomplete_fields = ['skill']
    classes = ['unfold-inline']
    show_change_link = True
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        class CustomForm(formset.form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if self.instance and self.instance.skill:
                    icon = self.instance.skill.icon or 'heroicons:academic-cap'
                    self.fields['skill'].widget.attrs.update({
                        'data-icon': icon,
                        'class': 'skill-select unfold-inline-field'
                    })
        formset.form = CustomForm
        return formset

    class Media:
        extend = True
        js = [
            'https://code.iconify.design/iconify-icon/2.3.0/iconify-icon.min.js',
            'js/admin/job_skill_inline.js'
        ]
        css = {
            'all': ('css/admin/job_skill_inline.css',)
        }


@admin.register(JobPosting)
class JobPostingAdmin(ModelAdmin):
    class Media:
        js = ['https://code.iconify.design/iconify-icon/2.3.0/iconify-icon.min.js']

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
