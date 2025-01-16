from django import forms
import openai
import json
import logging
import re  # Add this import
import tagulous.models
import tagulous.forms
from django.conf import settings
from .models import JobPosting

logger = logging.getLogger(__name__)

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
    paste = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'id_paste',
            'placeholder': 'Paste job description here to auto-fill fields',
            'rows': 8,
            'class': 'textarea textarea-bordered w-full font-mono'
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        for field in ['title', 'company', 'location']:
            self.fields[field].required = True

    def extract_field_value(self, text, field_name):
        """Extract field value from AI response"""
        pattern = rf"{field_name}:\s*(.+?)(?=\n\w+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def parse_job_with_ai(self, text):
        """Extract job details from text and return form-ready values"""
        if not text or not text.strip():
            return {'error': 'Empty job description provided'}

        try:
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY
            )

            prompt = """Extract the following job details:
Title: The exact job title
Company: The company name
Location: City/Region and work type (remote/hybrid/onsite)
Salary: Any salary or compensation details
Description: A well-formatted job description

Format each field on a new line starting with the field name."""

            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are a job details extractor. Extract and format the key details clearly."},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=2000
            )

            result = response.choices[0].message.content.strip()
            
            # Extract fields using regex
            data = {
                'title': self.extract_field_value(result, 'Title'),
                'company': self.extract_field_value(result, 'Company'),
                'location': self.extract_field_value(result, 'Location'),
                'salary_range': self.extract_field_value(result, 'Salary'),
                'description': self.extract_field_value(result, 'Description')
            }

            # Validate required fields
            required = ['title', 'company', 'location']
            if not all(data[key] for key in required):
                missing = [key for key in required if not data[key]]
                return {'error': f'Missing required fields: {", ".join(missing)}'}

            return {
                'status': 'success',
                'data': data
            }

        except Exception as e:
            logger.exception("Error in parse_job_with_ai")
            return {'error': str(e)}

    def clean(self):
        cleaned_data = super().clean()
        logger.debug(f"Cleaning form data: {cleaned_data}")
        
        # Ensure required fields are present
        required_fields = ['title', 'company', 'location']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'This field is required.')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        logger.debug(f"Saving form instance: {instance.__dict__}")
        
        if commit:
            instance.save()
            logger.debug(f"Instance saved with ID: {instance.id}")
            
        return instance

    class Meta:
        model = JobPosting
        fields = ['paste', 'title', 'company', 'location', 'url', 'salary_range', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'required': True,
                'id': 'id_title',  # Explicitly set ID
                'name': 'title',  # Ensure the name attribute is set
                'placeholder': 'e.g. Senior Developer, UX Designer',
                'class': 'input input-bordered w-full'
            }),
            'company': forms.TextInput(attrs={
                'required': True,
                'id': 'id_company',  # Explicitly set ID
                'name': 'company',  # Ensure the name attribute is set
                'placeholder': 'e.g. Toyota, Google, Tata',
                'class': 'input input-bordered w-full'
            }),
            'location': forms.TextInput(attrs={
                'required': True,
                'id': 'id_location',  # Explicitly set ID
                'name': 'location',  # Ensure the name attribute is set
                'placeholder': 'e.g. Tokyo, Berlin (Remote)',
                'class': 'input input-bordered w-full'
            }),
            'url': forms.URLInput(attrs={
                'id': 'id_url',  # Explicitly set ID
                'name': 'url',  # Ensure the name attribute is set
                'placeholder': 'Job posting URL',
                'class': 'input input-bordered w-full'
            }),
            'salary_range': forms.TextInput(attrs={
                'id': 'id_salary_range',  # Explicitly set ID
                'name': 'salary_range',  # Ensure the name attribute is set
                'placeholder': 'e.g. €45-65k/yr, $5-7k/mo',
                'class': 'input input-bordered w-full'
            }),
            'description': forms.Textarea(attrs={
                'id': 'id_description',  # Explicitly set ID
                'name': 'description',  # Ensure the name attribute is set
                'placeholder': '• Key responsibilities\n• Required skills\n• Benefits\n• How to apply',
                'rows': 12,
                'class': 'textarea textarea-bordered w-full font-mono'
            }),
            'status': forms.Select(attrs={
                'id': 'id_status',  # Explicitly set ID
                'name': 'status',  # Ensure the name attribute is set
                'class': 'select select-bordered w-full'
            })
        }
