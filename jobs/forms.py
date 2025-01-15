from django import forms
import openai
import json
import logging
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
            'placeholder': 'Paste job description here to auto-fill fields',
            'rows': 8,
            'class': 'textarea textarea-bordered w-full font-mono'
        }),
        required=False
    )

    def parse_job_with_ai(self, text):
        try:
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY
            )

            prompt = """Analyze the job posting and extract information into a structured format. Follow these rules strictly:

1. Extract only the main job title (e.g. "Senior Software Engineer", "Product Manager")
2. Company name should be just the organization name
3. Location should include city/state/country and work type (remote/hybrid/onsite)
4. Salary should only include compensation details
5. Description should be organized into sections, written professionally and extensively, formatted in pretty Markdown

Format the response exactly like this:
{
    "title": "ONLY the job position title",
    "company": "ONLY the company name",
    "location": "Location and work type",
    "salary_range": "Compensation details",
    "description": "- Overview:\\n  - Brief role summary\\n- Responsibilities:\\n  - Key duties\\n- Requirements:\\n  - Required skills\\n  - Experience needed\\n- Benefits:\\n  - Compensation\\n  - Perks"
}

Important:
- Title field must contain ONLY the job position/title
- Do not include company name or location in title
- Keep each field focused on its specific information
- Use clear section headers in description"""

            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are a precise job posting parser. Extract information accurately and keep each field focused on its specific purpose."},
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Parse this job posting:\n\n{text}"}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content.strip()
            logger.debug(f"Raw AI response: {result}")
            
            try:
                parsed = json.loads(result, strict=True)
                
                # Additional title cleaning
                if parsed.get('title'):
                    # Remove common extras from title
                    title = parsed['title']
                    title = title.split(' - ')[0]  # Remove anything after hyphen
                    title = title.split(' at ')[0]  # Remove "at Company"
                    title = title.split(' in ')[0]  # Remove location
                    title = title.strip()
                    parsed['title'] = title
                
                # Validate and clean the parsed data
                cleaned_parsed = {}
                default_values = {
                    'title': 'Position not specified',
                    'company': 'Company not specified',
                    'location': 'Location not specified',
                    'salary_range': 'Salary not disclosed',
                    'description': 'No detailed description provided'
                }
                
                for key in default_values.keys():
                    value = parsed.get(key, default_values[key])
                    if isinstance(value, (dict, list)):
                        # Handle structured data
                        if key == 'description':
                            # Convert structured description to formatted text
                            if isinstance(value, dict):
                                sections = []
                                for section, content in value.items():
                                    sections.append(f"- {section}:")
                                    if isinstance(content, list):
                                        sections.extend(f"  - {item}" for item in content)
                                    else:
                                        sections.append(f"  - {content}")
                                cleaned_value = '\n'.join(sections)
                            elif isinstance(value, list):
                                cleaned_value = '\n'.join(f"- {item}" for item in value)
                        else:
                            cleaned_value = str(value)
                    else:
                        cleaned_value = str(value).strip()
                    
                    # Clean string values
                    cleaned_value = cleaned_value.replace('\\n', '\n').replace('\\', '')
                    cleaned_value = cleaned_value.replace('"', "'")
                    
                    # Ensure proper formatting for description
                    if key == 'description':
                        lines = cleaned_value.split('\n')
                        formatted_lines = []
                        for line in lines:
                            line = line.strip()
                            if line:
                                if not line.startswith('-'):
                                    line = f"- {line}"
                                formatted_lines.append(line)
                        cleaned_value = '\n'.join(formatted_lines)
                    
                    cleaned_parsed[key] = cleaned_value or default_values[key]
                
                logger.debug(f"Cleaned parsed data: {cleaned_parsed}")
                return cleaned_parsed
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}\nResponse: {result}")
                return None
                
        except Exception as e:
            logger.error(f"AI processing error: {str(e)}")
            raise forms.ValidationError(f"Error processing job description: {str(e)}")

    def clean(self):
        cleaned_data = super().clean()
        paste_text = cleaned_data.get('paste')

        # Skip validation for AI processing
        if self.data.get('process_paste') == 'true':
            # Clear any validation errors
            self._errors = {}
            return cleaned_data  # return cleaned_data, not self.data

        # Normal form validation
        if paste_text:
            parsed = self.parse_job_with_ai(paste_text)
            if parsed:
                # Only update empty fields with parsed content
                if not cleaned_data.get('title'):
                    cleaned_data['title'] = parsed.get('title', '')
                if not cleaned_data.get('company'):
                    cleaned_data['company'] = parsed.get('company', '')
                if not cleaned_data.get('location'):
                    cleaned_data['location'] = parsed.get('location', '')
                if not cleaned_data.get('salary_range'):
                    cleaned_data['salary_range'] = parsed.get('salary_range', '')
                if not cleaned_data.get('description'):
                    cleaned_data['description'] = parsed.get('description', '')

        # Log the data being processed
        logger.debug(f"Form data being processed: {self.data}")
        logger.debug(f"Cleaned data: {cleaned_data}")
        
        # Ensure required fields are present
        required_fields = ['title', 'company', 'location']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'This field is required.')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Log the instance data before saving
        logger.debug(f"Instance data before save: {instance.__dict__}")
        
        if commit:
            instance.save()
            logger.debug(f"Instance saved successfully: {instance.id}")
            
        return instance

    class Meta:
        model = JobPosting
        fields = ['paste', 'title', 'company', 'location', 'url', 'salary_range', 'description', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'id': 'id_title',  # Explicitly set ID
                'placeholder': 'e.g. Senior Developer, UX Designer',
                'class': 'input input-bordered w-full'
            }),
            'company': forms.TextInput(attrs={
                'id': 'id_company',  # Explicitly set ID
                'placeholder': 'e.g. Toyota, Google, Tata',
                'class': 'input input-bordered w-full'
            }),
            'location': forms.TextInput(attrs={
                'id': 'id_location',  # Explicitly set ID
                'placeholder': 'e.g. Tokyo, Berlin (Remote)',
                'class': 'input input-bordered w-full'
            }),
            'url': forms.URLInput(attrs={
                'id': 'id_url',  # Explicitly set ID
                'placeholder': 'Job posting URL',
                'class': 'input input-bordered w-full'
            }),
            'salary_range': forms.TextInput(attrs={
                'id': 'id_salary_range',  # Explicitly set ID
                'placeholder': 'e.g. €45-65k/yr, $5-7k/mo',
                'class': 'input input-bordered w-full'
            }),
            'description': forms.Textarea(attrs={
                'id': 'id_description',  # Explicitly set ID
                'placeholder': '• Key responsibilities\n• Required skills\n• Benefits\n• How to apply',
                'rows': 12,
                'class': 'textarea textarea-bordered w-full font-mono'
            }),
            'status': forms.Select(attrs={
                'id': 'id_status',  # Explicitly set ID
                'class': 'select select-bordered w-full'
            })
        }