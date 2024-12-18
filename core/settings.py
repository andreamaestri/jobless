// ...existing code...

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [...],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                // ...existing context processors...
                'core.context_processors.navigation',
            ],
        },
    },
]

// ...existing code...
