from django import forms
from django_summernote.widgets import SummernoteWidget
from crispy_forms.helper import FormHelper
from .models import Event
from django.utils import timezone


class EventForm(forms.ModelForm):
    BASE_CLASS = (
        "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
        "focus:border-blue-500 focus:ring-blue-500"
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

    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter event date and time'
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


    class Meta:
        model = Event
        fields = [
            'title', 'event_type', 'date', 'location', 'notes', 'job_posting'
        ]
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'space-y-4'
