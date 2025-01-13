from django import forms
from django.urls import reverse_lazy
from django_summernote.widgets import SummernoteWidget
from crispy_forms.helper import FormHelper
from .models import JobPosting, SkillsTagModel
import tagulous.models
import tagulous.forms

class CustomTagWidget(tagulous.forms.TagWidget):
    template_name = 'jobs/widgets/tag_widget.html'
    
    class Media:
        js = [
            'js/skill-icons.js',  # You'll need to create this file with the SKILL_ICONS data
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_options = tagulous.models.TagOptions(
            autocomplete_view='jobs:skills_autocomplete',
            force_lowercase=True,
            space_delimiter=False,
            max_count=10
        )

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'company', 'location', 'url', 'salary_range', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Senior Software Engineer',
                'class': 'input input-bordered w-full'
            }),
            'company': forms.TextInput(attrs={
                'placeholder': 'e.g. Acme Corp',
                'class': 'input input-bordered w-full'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g. San Francisco, CA or Remote',
                'class': 'input input-bordered w-full'
            }),
            'url': forms.URLInput(attrs={
                'placeholder': 'https://',
                'class': 'input input-bordered w-full'
            }),
            'salary_range': forms.TextInput(attrs={
                'placeholder': 'e.g. $100,000 - $150,000',
                'class': 'input input-bordered w-full'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter the job description...',
                'rows': 10,
                'class': 'textarea textarea-bordered w-full font-mono'
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            })
        }