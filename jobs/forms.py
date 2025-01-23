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
        for field in ['title', 'company', 'location', 'status']:
            self.fields[field].required = True
            
        # Set default status if not provided
        if not self.initial.get('status'):
            self.initial['status'] = 'draft'


    def parse_job_with_ai(self, text):
        """Extract job details using AI-first approach"""
        if not text or not text.strip():
            return {'error': 'Empty job description provided'}

        # Basic text cleanup
        text = self._basic_cleanup(text)
        
        try:
            # Let GPT do the heavy lifting
            parsed_data = self._parse_with_gpt(text)
            
            if not parsed_data:
                return {
                    'error': 'Failed to parse job description',
                    'details': 'AI parsing failed'
                }

            # Format the response
            form_data = {
                'title': parsed_data.get('title', ''),
                'company': parsed_data.get('company', ''),
                'location': parsed_data.get('location', ''),
                'salary_range': parsed_data.get('salary', ''),
                'description': self._format_description(text, parsed_data.get('sections', {})),
                'status': 'NEW'
            }

            # Validation
            missing = [f for f in ['title', 'company', 'location'] if not form_data[f]]
            if missing:
                return {
                    'error': f"Missing required fields: {', '.join(missing)}",
                    'partial_data': form_data,
                    'missing_fields': missing
                }

            return {'status': 'success', 'data': form_data}

        except Exception as e:
            logger.exception("Error in parse_job_with_ai")
            return {'error': str(e), 'details': "Failed to process job description"}

    def _basic_cleanup(self, text):
        """Minimal text cleanup to preserve structure"""
        return (text.replace('\r\n', '\n')
                   .replace('\r', '\n')
                   .strip())

    def _parse_with_gpt(self, text):
        """Use GPT to extract all relevant information"""
        try:
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY
            )

            prompt = """
            Parse this job posting and extract the following information in JSON format:
            {
                "title": "exact job title without dates/salary",
                "company": "company name only",
                "location": "location with work model (Remote/Hybrid/On-site)",
                "salary": "normalized salary in K format if available",
                "sections": {
                    "about": "about the role/position text",
                    "responsibilities": "key responsibilities text",
                    "requirements": "requirements/qualifications text",
                    "benefits": "benefits/perks text"
                }
            }

            Rules:
            1. Keep title, company, location short and precise
            2. Format salary as "£50K" or "£50K-60K/year" if available
            3. Preserve proper formatting in section texts
            4. Return strict JSON format
            5. Strip company name of legal suffixes (Ltd, Inc, etc)
            6. Format location as "City, Country" or "City-based, Remote/Hybrid"
            7. Include currency symbol in salary
            8. Organize description into clear sections

            Job posting:
            """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a precise job posting parser that returns only valid JSON."},
                    {"role": "user", "content": prompt + "\n\n" + text}
                ],
                temperature=0.1
            )

            # Parse JSON response
            try:
                parsed = json.loads(response.choices[0].message.content)
                logger.debug("GPT parsed result: %s", json.dumps(parsed, indent=2))
                return parsed
            except json.JSONDecodeError:
                logger.error("Failed to parse GPT response as JSON")
                return None

        except Exception as e:
            logger.exception("GPT parsing failed")
            return None

    def _format_description(self, original_text, sections):
        """Format the description with sections"""
        formatted = []

        # Add structured sections
        for section_name in ['about', 'responsibilities', 'requirements', 'benefits']:
            content = sections.get(section_name, '').strip()
            if content:
                title = section_name.replace('_', ' ').title()
                formatted.append(f"• {title}:\n{content}")

        # If no sections parsed, use original text
        if not formatted:
            return original_text.strip()

        return "\n\n".join(formatted)

    def clean(self):
        cleaned_data = super().clean()
        logger.debug(f"Cleaning form data: {cleaned_data}")
        
        # Handle skills field specially
        skills_data = cleaned_data.get('skills', '')
        if skills_data:
            try:
                # Log raw skills data
                logger.debug(f"Raw skills data: {skills_data}")
                
                # Split comma-separated string into list
                skills = [s.strip().lower() for s in skills_data.split(',') if s.strip()]
                cleaned_data['skills'] = skills
                
                # Log processed skills as JSON
                logger.debug(f"Processed skills (JSON): {json.dumps(skills, indent=2)}")
            except Exception as e:
                logger.error(f"Error processing skills: {e}")
                self.add_error('skills', 'Invalid skills format')
        
        # Check required fields
        required_fields = ['title', 'company', 'location', 'status']
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
                # Handle skills as list of strings
                if 'skills' in self.cleaned_data:
                    skills = self.cleaned_data['skills']
                    if skills:
                        # Log skills before saving
                        logger.info(f"Setting skills (JSON): {json.dumps(skills, indent=2)}")
                        
                        # Get current skills for comparison
                        current_skills = list(instance.skills.values_list('name', flat=True))
                        logger.info(f"Current skills before update (JSON): {json.dumps(current_skills, indent=2)}")
                        
                        # Save new skills
                        instance.skills.set(skills)
                        
                        # Get saved skills
                        saved_skills = list(instance.skills.values_list('name', flat=True))
                        logger.info(f"Saved skills after update (JSON): {json.dumps(saved_skills, indent=2)}")
                        
                        # Log skill changes
                        added = set(skills) - set(current_skills)
                        removed = set(current_skills) - set(skills)
                        if added:
                            logger.info(f"Added skills: {json.dumps(list(added), indent=2)}")
                        if removed:
                            logger.info(f"Removed skills: {json.dumps(list(removed), indent=2)}")
                    else:
                        # Log clearing all skills
                        current_skills = list(instance.skills.values_list('name', flat=True))
                        logger.info(f"Clearing all skills (JSON): {json.dumps(current_skills, indent=2)}")
                        instance.skills.clear()
                        logger.info("All skills cleared successfully")
                self.save_m2m()
                logger.info(f"Successfully saved job posting with ID: {instance.id}")
        except Exception as e:
            logger.exception("Error saving job posting")
            raise
            
        return instance

    class Meta:
        model = JobPosting
        fields = ['title', 'company', 'location', 'url', 'salary_range', 'description', 'status', 'skills']
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
            }),
            'skills': CustomTagWidget(attrs={
                'id': 'id_skills',
                'name': 'skills',
                'class': 'input input-bordered w-full',
                'placeholder': 'Add skills (e.g., Python, React, AWS)'
            })
        }
