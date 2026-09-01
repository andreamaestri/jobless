from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm


class SignupForm(SignupForm):
    first_name = forms.CharField(
        label=_("First name"),
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': _("Your first name"),
            'autocomplete': 'given-name',
        }),
    )
    last_name = forms.CharField(
        label=_("Surname"),
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _("Your surname"),
            'autocomplete': 'family-name',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["class"] = "input w-full"
        self.fields["last_name"].widget.attrs["class"] = "input w-full"
        self.field_order = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class SearchFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search jobs, companies, contacts...',
            'class': 'grow',
            'id': 'searchInput',
            'autocomplete': 'off'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + [
            ('interested', 'Interested'),
            ('applied', 'Applied'),
            ('interviewing', 'Interviewing'),
            ('rejected', 'Rejected'),
            ('hired', 'Hired'),
        ]
    )
    
    type = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Types'),
            ('jobs', 'Jobs'),
            ('events', 'Events'),
            ('contacts', 'Contacts'),
        ]
    )
