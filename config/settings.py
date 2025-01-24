import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Find the INSTALLED_APPS section and add django_components
INSTALLED_APPS = [
    # ... existing apps ...
    'django_components',
    'django_components.safer_template_loader',
]

# Add template configuration for django-components
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'jobs' / 'components',  # Add components directory
        ],
        'OPTIONS': {
            'context_processors': [
                # ... existing context processors ...
            ],
            'loaders': [
                'django_components.template_loader.ComponentLoader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

# Django-components settings
DJANGO_COMPONENTS = {
    'AUTODISCOVER': True,
    'AUTODISCOVER_DIRS': ['components'],
}
