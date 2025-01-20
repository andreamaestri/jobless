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
    paste_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'paste',
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

            # Improved prompt with clearer structure
            prompt = """Extract these job details from the provided job posting.
Use this exact format for your response, keeping the exact field names:

Title: [extract the job title]
Company: [extract the company name]
Location: [extract the location, including remote if applicable]
Salary: [extract salary information if present, or leave blank]
Description:
[extract and format the full job description, maintaining the original structure]

Include all requirements, responsibilities, and benefits in the Description section."""

            # Get AI response
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a precise job details extractor. Extract and format job posting details exactly as requested."},
                    {"role": "user", "content": f"{prompt}\n\nJob Posting:\n{text}"}
                ],
                temperature=0.1,  # Slightly higher temperature for better extraction
                max_tokens=2000
            )

            # Get response text
            extracted = response.choices[0].message.content.strip()
            logger.debug(f"AI Response:\n{extracted}")

            # Initialize form data
            form_data = {
                'title': '',
                'company': '',
                'location': '',
                'salary_range': '',
                'description': '',
                'status': 'NEW'
            }

            # Parse AI response into fields
            current_field = None
            description_lines = []
            
            for line in extracted.split('\n'):
                line = line.strip()
                
                if not line:
                    continue
                    
                # Check for field headers
                if line.startswith('Title:'):
                    current_field = 'title'
                    form_data['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Company:'):
                    current_field = 'company'
                    form_data['company'] = line.replace('Company:', '').strip()
                elif line.startswith('Location:'):
                    current_field = 'location'
                    form_data['location'] = line.replace('Location:', '').strip()
                elif line.startswith('Salary:'):
                    current_field = 'salary_range'
                    form_data['salary_range'] = line.replace('Salary:', '').strip()
                elif line.startswith('Description:'):
                    current_field = 'description'
                elif current_field == 'description':
                    description_lines.append(line)

            # Process description
            if description_lines:
                # Clean and format description
                description = '\n'.join(description_lines).strip()
                # Convert lists to bullet points
                description = re.sub(r'(?m)^[-•*]\s*', '• ', description)
                description = re.sub(r'(?m)^(\d+\.|\w+\.)\s+', '• ', description)
                form_data['description'] = description

            # Validate required fields
            required = ['title', 'company', 'location']
            missing = [f for f in required if not form_data.get(f)]
            if missing:
                error_msg = f"Could not extract these required fields: {', '.join(missing)}"
                logger.error(f"Validation failed: {error_msg}")
                return {'error': error_msg}

            logger.info("Successfully extracted all required fields")
            return {'status': 'success', 'data': form_data}

        except Exception as e:
            error_msg = "Failed to process job description. Please try again or fill in the fields manually."
            if isinstance(e, (openai.APIError, openai.APITimeoutError, openai.APIConnectionError)):
                error_msg = "AI service is temporarily unavailable. Please try again later."
            
            logger.exception(f"Error in parse_job_with_ai: {str(e)}")
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
        fields = ['title', 'company', 'location', 'url', 'salary_range', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'required': True,
                'id': 'id_title',
                'name': 'title',
                'placeholder': 'Job title (e.g., Senior Python Developer, UI/UX Designer)',
                'class': 'input input-bordered w-full'
            }),
            'company': forms.TextInput(attrs={
                'required': True,
                'id': 'id_company',
                'name': 'company',
                'placeholder': 'Company name (e.g., Microsoft, Apple, Amazon)',
                'class': 'input input-bordered w-full'
            }),
            'location': forms.TextInput(attrs={
                'required': True,
                'id': 'id_location',
                'name': 'location',
                'placeholder': 'Location (e.g., San Francisco, Remote, London UK)',
                'class': 'input input-bordered w-full'
            }),
            'url': forms.URLInput(attrs={
                'id': 'id_url',
                'name': 'url',
                'placeholder': 'Link to original job posting (https://...)',
                'class': 'input input-bordered w-full'
            }),
            'salary_range': forms.TextInput(attrs={
                'id': 'id_salary_range',
                'name': 'salary_range',
                'placeholder': 'Salary range (e.g., $80K-120K/year, €50-60K, Competitive)',
                'class': 'input input-bordered w-full'
            }),
            'description': forms.Textarea(attrs={
                'id': 'id_description',
                'name': 'description',
                'data-field': 'description',
                'placeholder': '• About the Role:\n• Key Responsibilities:\n• Required Skills:\n• Nice to Have:\n• Benefits & Perks:\n• How to Apply:',
                'rows': 12,
                'class': 'textarea textarea-bordered w-full font-mono'
            }),
            'status': forms.Select(attrs={
                'id': 'id_status',
                'name': 'status',
                'class': 'select select-bordered w-full'
            })
        }
