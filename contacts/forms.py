from django import forms
from django_summernote.widgets import SummernoteWidget
from crispy_forms.helper import FormHelper
from django.utils.translation import gettext_lazy as _
from .models import Contact


class ContactForm(forms.ModelForm):
    BASE_CLASS = (
        "w-full rounded-xl border-base-300 bg-base-100 px-4 py-3 "
        "text-base-content shadow-sm focus:border-primary focus:ring-primary "
        "placeholder-base-content/50 text-sm"
    )

    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': _('Enter contact name')
        })
    )

    company = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': _('Enter company')
        })
    )

    position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': _('Enter position')
        })
    )

    email = forms.EmailField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': _('Enter email address')
        })
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': _('Enter phone number')
        })
    )

    linkedin = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': BASE_CLASS}),
    )

    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': BASE_CLASS,
        })
    )

    class Meta:
        model = Contact
        fields = [
            'name', 'company', 'position', 'email',
            'phone', 'linkedin', 'notes',
        ]
        labels = {
            'name': _('Name'),
            'company': _('Company'),
            'position': _('Position'),
            'email': _('Email address'),
            'phone': _('Phone number'),
            'linkedin': _('LinkedIn profile'),
            'notes': _('Notes'),
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'space-y-4'
