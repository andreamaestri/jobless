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
    BASE_CLASS = (
        "w-full rounded-xl border-base-300 bg-base-100 px-4 py-3 "
        "text-base-content shadow-sm focus:border-primary focus:ring-primary "
        "placeholder-base-content/50 text-sm"
    )

    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter job title'
        })
    )

    company = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter company name'
        })
    )

    location = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter job location'
        })
    )

    salary_range = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'e.g., £30,000 - £40,000'
        })
    )

    url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter job posting URL'
        })
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': BASE_CLASS,
            'rows': 5,
            'placeholder': 'Enter job description'
        })
    )

    status = forms.ChoiceField(
        choices=JobPosting.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': BASE_CLASS,
        })
    )

    # Use the model's TagField directly
    skills = JobPosting._meta.get_field('skills').formfield(
        widget=forms.SelectMultiple(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Select skills...',
            'multiple': 'multiple'
        })
    )

    class Meta:
        model = JobPosting
        fields = [
            'title', 'company', 'location', 'salary_range',
            'url', 'description', 'skills', 'status'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'space-y-4'

        # Apply base class to all fields except skills
        for field_name, field in self.fields.items():
            if field_name != 'skills':
                field.widget.attrs['class'] = self.BASE_CLASS