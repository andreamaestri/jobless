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
        
        # Use hidden input for skills - will be managed by modal
        self.fields['skills'] = forms.CharField(
            required=False,
            widget=forms.HiddenInput(attrs={
                'id': 'id_skills',
                'name': 'skills',
                'class': 'skills-input'
            })
        )

    def parse_job_with_ai(self, text):
        """Extract job details from any copy-pasted content format"""
        if not text or not text.strip():
            return {'error': 'Empty job description provided'}

        logger.debug(f"Processing job description:\n{text[:500]}...")

        # Enhanced field patterns for better recognition
        FIELD_PATTERNS = {
            'title': [
                r'(?i)^.*?(position|job title|role):\s*(.+?)(?=\n|$)',
                r'(?i)^.*?hiring.*?(for|a)\s+(.+?)(?=\n|$)',
                r'(?i)^.*?seeking.*?(a)\s+(.+?)(?=\n|$)',
                r'(?i)^((?!location|company|salary).+?)(?=\n|$)'  # Fallback to first line
            ],
            'company': [
                r'(?i)(?:^|\n).*?company:\s*(.+?)(?=\n|$)',
                r'(?i)(?:^|\n).*?employer:\s*(.+?)(?=\n|$)',
                r'(?i)(?:^|\n).*?at\s+([^|,\n]+)(?:\||,|\n|$)',
                r'(?i)(?:^|\n)([^|,\n]+?)\s+is\s+(?:hiring|seeking|looking)'
            ],
            'location': [
                r'(?i)(?:^|\n).*?location:\s*(.+?)(?=\n|$)',
                r'(?i)(?:^|\n).*?\b(?:in|at)\s+(remote|[^,\n]+(?:,\s*[^,\n]+){0,2})(?=\n|$)',
                r'(?i)(?:^|\n).*?(?:position|job)\s+(?:in|at)\s+([^,\n]+(?:,\s*[^,\n]+){0,2})(?=\n|$)',
                r'(?i)(?:hybrid|remote|on-?site)\s*(?:in\s+)?([^,\n]+(?:,\s*[^,\n]+){0,2})'
            ],
            'salary_range': [
                r'(?i)(?:^|\n).*?salary:\s*(.+?)(?=\n|$)',
                r'(?i)(?:^|\n).*?compensation:\s*(.+?)(?=\n|$)',
                r'(?i)(?:^|\n).*?\$[\d,.]+\s*[-–]\s*\$[\d,.]+\s*(?:k|K|,000)?(?:/(?:year|yr|annual|annually))?',
                r'(?i)(?:^|\n).*?(?:\$[\d,.]+\s*(?:k|K|,000)?(?:/(?:year|yr|annual|annually))?)'
            ]
        }

        try:
            # Initialize OpenAI client and get initial response
            client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY
            )

            # Updated prompt to avoid redundant labels
            prompt = """Extract and format the job posting details with only the description in markdown:

[Job Title as plain text]

[Company Name as plain text]

[Location as plain text]

[Salary if specified as plain text]

# About the Role
[Overview of the position in markdown]

## Key Responsibilities
* [List main duties]

## Requirements
* [List required skills/experience]

## Nice to Have
* [List preferred qualifications]

## Benefits & Perks
* [List benefits/perks]

Format the first 4 lines without labels or markdown, and use markdown only for the description."""

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

            # Get response text and split into lines
            extracted = response.choices[0].message.content.strip()
            logger.debug(f"AI Response:\n{extracted}")
            lines = extracted.split('\n')

            # Initialize form data
            form_data = {
                'title': '',
                'company': '',
                'location': '',
                'salary_range': '',
                'description': '',
                'status': 'NEW'
            }

            section_count = 0
            description_started = False
            description_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    if description_started:
                        description_lines.append('')
                    continue

                # Detect if we've reached the description (starts with # or ## or "About")
                if line.startswith('#') or line.lower().startswith('about'):
                    description_started = True
                    description_lines.append(line)
                    continue

                if description_started:
                    description_lines.append(line)
                    continue

                # Process header fields (first 4 non-empty lines)
                if section_count == 0:
                    form_data['title'] = line
                    section_count += 1
                elif section_count == 1:
                    form_data['company'] = line
                    section_count += 1
                elif section_count == 2:
                    form_data['location'] = line
                    section_count += 1
                elif section_count == 3 and ('$' in line or 'salary' in line.lower() or 'compensation' in line.lower()):
                    form_data['salary_range'] = line
                    section_count += 1
                elif not description_started and line:
                    # If we haven't started description but have all fields, this must be description
                    description_started = True
                    description_lines.append(line)

            # Add improved salary patterns
            SALARY_PATTERNS = [
                r'(?:^|\n).*?(?:salary|compensation):\s*((?:£|\$|€)?[,\d]+(?:[kK])?(?:\s*-\s*(?:£|\$|€)?[,\d]+(?:[kK])?)?(?:/\w+)?)',
                r'(?:^|\n)\s*((?:£|\$|€)?[,\d]+(?:[kK])?(?:\s*-\s*(?:£|\$|€)?[,\d]+(?:[kK])?)?(?:/\w+)?)\s*(?:\n|$)',
                r'(?:^|\n).*?(?:salary|compensation|pay).*?((?:£|\$|€)?[,\d]+(?:[kK])?(?:\s*-\s*(?:£|\$|€)?[,\d]+(?:[kK])?)?(?:/\w+)?)',
                r'(?:^|\n).*?(?:£|\$|€)?[,\d]+(?:[kK])?(?:\s*-\s*(?:£|\$|€)?[,\d]+(?:[kK])?)?(?:/\w+)?'
            ]

            # Extract salary from description if not found in header
            if not form_data['salary_range'] and description_lines:
                description_text = '\n'.join(description_lines[:10])  # Check first 10 lines
                for pattern in SALARY_PATTERNS:
                    salary_match = re.search(pattern, description_text, re.IGNORECASE)
                    if salary_match:
                        salary = salary_match.group(1) if len(salary_match.groups()) > 0 else salary_match.group(0)
                        form_data['salary_range'] = salary.strip()
                        
                        # Remove the salary from the beginning of description if found there
                        if description_lines and salary in description_lines[0:3]:
                            description_lines = [line for line in description_lines 
                                              if not any(s in line for s in [salary, 'salary:', 'compensation:'])]
                        break

            # Process description after salary extraction
            if description_lines:
                description = '\n'.join(description_lines)
                
                # Ensure description starts with proper header if missing
                if not description.startswith('# ') and not description.startswith('## '):
                    description = '# About the Role\n\n' + description
                
                # Clean up markdown formatting
                description = re.sub(r'\n{3,}', '\n\n', description)  # Remove extra newlines
                description = re.sub(r'(?m)^[-•*]\s*', '* ', description)  # Standardize bullet points
                description = re.sub(r'(?m)^(\d+\.|\w+\.)\s+', '* ', description)  # Convert numbered lists
                
                form_data['description'] = description.strip()
                logger.debug(f"Processed description:\n{description[:500]}...")

            # Clean up fields
            for field in ['title', 'company', 'location', 'salary_range']:
                if form_data[field]:
                    # Remove common prefixes and clean up
                    form_data[field] = re.sub(r'^(?:title|company|location|salary):\s*', '', 
                                            form_data[field], flags=re.IGNORECASE)
                    form_data[field] = form_data[field].strip()

            # Clean up salary format
            if form_data['salary_range']:
                salary = form_data['salary_range']
                # Standardize format
                salary = re.sub(r'\s+', ' ', salary)  # Normalize whitespace
                salary = re.sub(r'(?<=\d)[kK](?=\s|$)', ',000', salary)  # Convert k/K to ,000
                salary = salary.strip('., ')  # Clean up edges
                
                # Add default currency if missing (assuming GBP)
                if not re.match(r'^(?:£|\$|€)', salary):
                    salary = f'£{salary}'
                
                form_data['salary_range'] = salary

            # Validate required fields
            required_fields = ['title', 'company', 'location']
            missing_fields = [f for f in required_fields if not form_data.get(f)]
            
            if missing_fields:
                return {
                    'error': f"Could not extract these required fields: {', '.join(missing_fields)}",
                    'partial_data': form_data,
                    'missing_fields': missing_fields
                }

            logger.info("Successfully extracted all required fields")
            return {
                'status': 'success',
                'data': form_data
            }

        except Exception as e:
            logger.exception("Error in parse_job_with_ai")
            return {
                'error': str(e),
                'details': "Failed to process job description"
            }

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
