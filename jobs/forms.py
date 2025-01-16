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

    def parse_job_with_ai(self, text):
        """Extract job details using AI and return form-ready data"""
        if not text or not text.strip():
            return {'error': 'Empty job description provided'}

        logger.debug(f"Processing job description:\n{text[:500]}...")

        try:
            # Initialize OpenAI client
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY
            )

            # Simple, direct prompt
            prompt = """Extract these job details into a clear format:
Title: [job title]
Company: [company name]
Location: [location]
Salary: [salary if listed]
Description: [full job description]"""

            # Get AI response
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "Extract job posting details in a clear format"},
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ],
                temperature=0
            )

            # Get response text
            extracted = response.choices[0].message.content.strip()
            logger.debug(f"AI Response:\n{extracted}")

            # Map response to form fields
            form_data = {
                'title': '',
                'company': '',
                'location': '',
                'salary_range': '',
                'description': '',
                'status': 'NEW'
            }

            # Parse AI response into fields
            lines = extracted.split('\n')
            in_description = False
            description_lines = []
            
            for line in lines:
                line = line.strip()
                
                # If we're in description mode, collect all non-empty lines
                if in_description:
                    if line and not any(line.startswith(f"{field}:") for field in ['Title', 'Company', 'Location', 'Salary']):
                        description_lines.append(line)
                    continue
                
                # Check for field headers
                if line.startswith('Title:'):
                    form_data['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Company:'):
                    form_data['company'] = line.replace('Company:', '').strip()
                elif line.startswith('Location:'):
                    form_data['location'] = line.replace('Location:', '').strip()
                elif line.startswith('Salary:'):
                    form_data['salary_range'] = line.replace('Salary:', '').strip()
                elif line.startswith('Description:') or line == 'Job Description:':
                    in_description = True
                    # If there's content after the Description: label, add it
                    content = line.replace('Description:', '').replace('Job Description:', '').strip()
                    if content:
                        description_lines.append(content)
            
            # Join all description lines
            if description_lines:
                form_data['description'] = '\n'.join(description_lines)

            # Format description with bullets if not empty
            if form_data['description']:
                form_data['description'] = '• ' + form_data['description'].replace('\n', '\n• ').strip('• ')

            # Validate required fields
            required = ['title', 'company', 'location']
            missing = [f for f in required if not form_data[f]]
            if missing:
                error_msg = f"Missing required fields: {', '.join(missing)}"
                logger.error(f"Validation failed: {error_msg}\nAI Response:\n{extracted}")
                return {'error': error_msg}

            logger.info("Successfully extracted all required fields")
            return {'status': 'success', 'data': form_data}

        except Exception as e:
            if isinstance(e, openai.APIError):
                error_msg = "AI service temporarily unavailable. Please try again later."
            elif isinstance(e, openai.APITimeoutError):
                error_msg = "Request timed out. Please try again."
            elif isinstance(e, openai.APIConnectionError):
                error_msg = "Connection error. Please check your internet connection."
            else:
                error_msg = f"Error processing job description: {str(e)}"
            
            logger.exception(error_msg)
            return {'error': error_msg}

    def clean(self):
        cleaned_data = super().clean()
        logger.debug(f"Cleaning form data: {cleaned_data}")
        
        # Ensure required fields are present
        required_fields = ['title', 'company', 'location']
        missing_fields = []
        for field in required_fields:
            if not cleaned_data.get(field):
                missing_fields.append(field)
                self.add_error(field, 'This field is required.')
        
        if missing_fields:
            logger.error(f"Missing required fields: {', '.join(missing_fields)}")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        logger.debug(f"Saving form instance: {instance.__dict__}")
        
        try:
            if commit:
                instance.save()
                logger.info(f"Successfully saved job posting with ID: {instance.id}")
        except Exception as e:
            logger.exception("Error saving job posting")
            raise
            
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
