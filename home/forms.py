from django import forms

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
