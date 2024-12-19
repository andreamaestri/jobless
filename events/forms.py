from django import forms
from django_summernote.widgets import SummernoteWidget
from crispy_forms.helper import FormHelper
from .models import Event
from jobs.models import JobPosting
from django.utils import timezone

class EventForm(forms.ModelForm):
    BASE_CLASS = (
        "w-full rounded-xl border-base-300 bg-base-100 px-4 py-3 "
        "text-base-content shadow-sm focus:border-primary focus:ring-primary "
        "placeholder-base-content/50 text-sm"
    )

    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter event title'
        })
    )

    event_type = forms.ChoiceField(
        choices=Event.EVENT_TYPES,
        widget=forms.Select(attrs={
            'class': BASE_CLASS,
            'id': 'status-select'
        })
    )

    date = forms.DateTimeField(  # Changed from DateField to DateTimeField
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': BASE_CLASS,
            'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
        })
    )

    location = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter event location'
        })
    )

    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': BASE_CLASS,
            'rows': 5,
            'placeholder': 'Enter notes'
        }),
        required=False
    )

    job_posting = forms.ModelChoiceField(
        queryset=JobPosting.objects.none(),  # Initialize with empty queryset
        widget=forms.Select(attrs={
            'class': BASE_CLASS,
        }),
        
    )

    class Meta:
        model = Event
        fields = [
            'title', 'event_type', 'date', 'location', 'notes', 'job_posting'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'space-y-4'
        
        if user:
            # Filter job postings for users
            self.fields['job_posting'].queryset = JobPosting.objects.filter(user=user)
        else:
            # Provide an empty queryset if no user
            self.fields['job_posting'].queryset = JobPosting.objects.none()