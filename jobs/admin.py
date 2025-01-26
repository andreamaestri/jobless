from django import forms
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
import tagulous.admin
from .models import JobPosting, SkillTreeModel, JobSkill


class SkillTreeModelForm(forms.ModelForm):
    class Meta:
        model = SkillTreeModel
        fields = '__all__'


@admin.register(SkillTreeModel)
class SkillTreeModelAdmin(tagulous.admin.TagModelAdmin, ModelAdmin):
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
