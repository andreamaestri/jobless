from django import forms
from django_summernote.widgets import SummernoteWidget
from crispy_forms.helper import FormHelper
from .models import Contact


class ContactForm(forms.ModelForm):
    BASE_CLASS = (
        "mt-1 block w-full rounded-md border-gray-300 shadow-sm "
        "focus:border-blue-500 focus:ring-blue-500"
    )

    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter contact name'
        })
    )

    company = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter company name'
        })
    )

    position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter contact position'
        })
    )

    email = forms.EmailField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter contact email address'
        })
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': BASE_CLASS,
            'placeholder': 'Enter contact phone number'
        })
    )

    linkedin = forms.URLField(
        required = False,
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
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'space-y-4'
