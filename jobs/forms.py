from django import forms
from django_summernote.widgets import SummernoteWidget
from crispy_forms.helper import FormHelper
from .models import JobPosting
from django.utils import timezone
import tagulous.models


class JobPostingForm(forms.ModelForm):
    BASE_CLASS = (
        "w-full rounded-xl border-[#e6d5cc] bg-white px-4 py-3 "
        "text-[#2c2c2c] shadow-sm focus:border-[#e28b67] focus:ring-[#e28b67] "
        "placeholder-[#999999] text-sm"
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

    skills = tagulous.models.TagField()
    

    status = forms.ChoiceField(
        choices=JobPosting.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': BASE_CLASS,
            'id': 'status-select'
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

        # Format skills as comma-separated string if instance exists
        if self.instance.pk and self.instance.skills:
            self.initial['skills'] = ', '.join(self.instance.skills.names())

    def clean_skills(self):
        """
        Convert comma-separated skills string to list and clean it
        """
        skills = self.cleaned_data.get('skills', '')
        if skills:
            # Split by comma, strip whitespace, and filter out empty strings
            return [
                skill.strip() 
                for skill in skills.split(',') 
                if skill.strip()
            ]
        return []