from django import forms
from django_summernote.widgets import SummernoteWidget
from crispy_forms.helper import FormHelper
from .models import JobPosting
import tagulous.models

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

        # Style the skills field
        self.fields['skills'].widget = forms.TextInput(attrs={
            'class': self.BASE_CLASS,
            'placeholder': 'Enter skills (comma-separated)'
        })

        # Properly handle the skills field for editing
        if self.instance.pk:
            self.initial['skills'] = ', '.join(str(tag) for tag in self.instance.skills.all())