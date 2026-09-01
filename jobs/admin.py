from django import forms
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
import django_tagulous.admin
from .models import JobPosting, SkillTreeModel, JobSkill


class SkillTreeModelForm(forms.ModelForm):
    class Meta:
        model = SkillTreeModel
        fields = '__all__'


@admin.register(SkillTreeModel)
class SkillTreeModelAdmin(django_tagulous.admin.TagModelAdmin, ModelAdmin):
    form = SkillTreeModelForm
    model = SkillTreeModel
    list_display = (
        'name',
        'label',
        'display_icon'
    )
    search_fields = ['name', 'label']
    list_filter = []
    ordering = ('name',)
    actions = ['merge_tags']
    prepopulated_fields = {}  # Override TagModelAdmin's default

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'label', 'icon'),
            'description': 'Basic skill information'
        }),
        ('Tags', {
            'fields': ('tags',),
            'description': 'Skill categorization'
        }),
        ('Additional Info', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

    tabs = [
        ("General", {'fieldsets': ['Basic Information']}),
        ("Settings", {'fieldsets': ['Tags']}),
        ("More", {'fieldsets': ['Additional Info']}),
    ]

    class Media:
        js = [
            'https://code.iconify.design/iconify-icon/2.3.0/'
            'iconify-icon.min.js'
        ]

    def display_icon(self, obj):
        if obj.icon:
            return format_html(
                '<div style="display: flex; align-items: center;">'
                '<iconify-icon icon="{}" width="20" '
                'height="20"></iconify-icon>'
                '<span>{}</span>'
                '</div>',
                obj.icon,
                obj.icon
            )
        return '-'
    display_icon.short_description = 'Icon'


@admin.register(JobSkill)
class JobSkillAdmin(ModelAdmin):
    model = JobSkill
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

    fieldsets = (
        ('Skill Details', {
            'fields': ('skill', 'proficiency'),
            'description': 'Main skill information'
        }),
        ('Job Association', {
            'fields': ('job',),
        }),
    )

    class Media:
        js = [
            'https://code.iconify.design/iconify-icon/2.3.0/'
            'iconify-icon.min.js'
        ]

    def skill_with_icon(self, obj):
        icon = (
            obj.skill.icon if obj.skill and obj.skill.icon
            else 'heroicons:academic-cap'
        )
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<iconify-icon icon="{}" style="margin-right: 8px" '
            'width="20"></iconify-icon>'
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

    class Media:
        js = [
            'https://code.iconify.design/iconify-icon/2.3.0/'
            'iconify-icon.min.js'
        ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "skill":
            kwargs["queryset"] = SkillTreeModel.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(JobPosting)
class JobPostingAdmin(ModelAdmin):
    model = JobPosting
    
    class Media:
        js = [
            'https://code.iconify.design/iconify-icon/2.3.0/'
            'iconify-icon.min.js'
        ]

    list_display = [
        'title',
        'company',
        'location',
        'status',
        'created_at',
        'updated_at'
    ]
    
    search_fields = ['title', 'company', 'description']
    list_filter = ['status', 'created_at', 'company']
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [JobSkillInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'company',
                'location'
            ),
            'description': 'Core job posting details'
        }),
        ('Details', {
            'fields': (
                'salary_range',
                'url',
                'description'
            ),
        }),
        ('Status', {
            'fields': (
                'status',
                'user'
            ),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',),
        }),
    )

    tabs = [
        ("Overview", {'fieldsets': ['Basic Information', 'Status']}),
        ("Details", {'fieldsets': ['Details'], 'inlines': ['JobSkillInline']}),
        ("History", {'fieldsets': ['Timestamps']}),
    ]

    # Actions
    actions = [
        'mark_as_applied',
        'mark_as_interviewing',
        'mark_as_rejected'
    ]
    
    def mark_as_applied(self, request, queryset):
        queryset.update(status='applied')
    mark_as_applied.short_description = "Mark selected jobs as Applied"
    
    def mark_as_interviewing(self, request, queryset):
        queryset.update(status='interviewing')
    mark_as_interviewing.short_description = (
        "Mark selected jobs as Interviewing"
    )
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = "Mark selected jobs as Rejected"


# ---------------------------------------------------------------------------
# Nachweis von Eigenbemühungen
# ---------------------------------------------------------------------------

from .models import (
    UserProfile,
    ObligationPlan,
    Application,
    EvidenceFile,
    AuditLog,
    Submission,
)


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'full_name', 'kundennummer', 'regime', 'office_name')
    search_fields = ('user__username', 'full_name', 'kundennummer')
    list_filter = ('regime',)


@admin.register(ObligationPlan)
class ObligationPlanAdmin(ModelAdmin):
    list_display = (
        'title', 'user', 'required_count', 'period', 'due_rule',
        'proof_form', 'valid_from', 'valid_to', 'is_active',
    )
    list_filter = ('period', 'due_rule', 'proof_form', 'is_active')
    search_fields = ('title', 'user__username', 'notes')


@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    list_display = (
        'applied_on', 'employer_name', 'job_title', 'user',
        'channel', 'result', 'effort_type',
    )
    list_filter = ('result', 'channel', 'effort_type', 'applied_on')
    search_fields = ('employer_name', 'job_title', 'user__username')
    date_hierarchy = 'applied_on'


@admin.register(EvidenceFile)
class EvidenceFileAdmin(ModelAdmin):
    list_display = ('filename', 'application', 'evidence_type', 'size', 'uploaded_at')
    list_filter = ('evidence_type',)
    search_fields = ('filename', 'application__employer_name')
    readonly_fields = ('sha256', 'mime', 'size', 'filename')


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ('user', 'application', 'action', 'field_name', 'created_at')
    search_fields = ('user__username', 'field_name')
    readonly_fields = ('user', 'application', 'action', 'field_name',
                       'old_value', 'new_value', 'created_at')


@admin.register(Submission)
class SubmissionAdmin(ModelAdmin):
    list_display = ('user', 'profile', 'period_from', 'period_to', 'submitted_on', 'rows')
    list_filter = ('profile',)
