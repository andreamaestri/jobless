# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jobless is a Django 5.1 application for tracking job search activities. Users can manage job postings, contacts, events, and use an AI assistant for CV feedback.

## Commands

### Development Server
```bash
python manage.py runserver
```

### Database Operations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test jobs
python manage.py test contacts
python manage.py test events
```

### Static Files & Frontend
```bash
# Collect static files
python manage.py collectstatic

# Build frontend assets (Vite)
npm run build

# Run Vite dev server (for hot reload)
npm run dev
```

### Tailwind CSS
```bash
python manage.py tailwind install
python manage.py tailwind build
```

## Architecture

### Django Apps
- **jobs** - Job postings with skills management, favorites, and status tracking
- **contacts** - Contact management linked to jobs
- **events** - Events calendar with job/contact associations
- **home** - Dashboard and navigation context processor
- **ai_assistant** - AI-powered CV feedback using OpenAI/Groq
- **theme** - Tailwind theme configuration
- **users** - User model extensions

### Key Models
- **JobPosting** - Central model with status workflow (interested → applied → interviewing → rejected/accepted)
- **SkillTreeModel** - Hierarchical skills using django-tagulous
- **JobSkill** - Through model linking jobs to skills with proficiency levels
- **Contact** - Network contacts with company/position info
- **Event** - Events with types (interview, meeting, followup, networking) linked to jobs and contacts

### Authentication
Uses django-allauth with multiple providers:
- Email/password authentication
- GitHub OAuth
- Google OAuth
- LinkedIn OpenID Connect

### Frontend Stack
- Tailwind CSS via django-tailwind
- Vite for asset bundling
- Alpine.js for interactivity
- HTMX for dynamic updates
- django-components for reusable UI components

### Storage
Production uses Oracle Cloud Object Storage (S3-compatible) via django-storages. Static files served via WhiteNoise.

### URL Namespacing
All apps use namespaced URLs (e.g., `jobs:list`, `contacts:detail`, `events:detail`).

## Environment Variables

Required for production:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Django secret key
- `GROQ_API_KEY` - For AI assistant
- `OCI_ACCESS_KEY`, `OCI_SECRET_KEY`, `OCI_BUCKET_NAME`, `OCI_NAMESPACE`, `OCI_REGION` - Object storage
- `GITHUB_CLIENT_ID`, `GITHUB_SECRET` - GitHub OAuth
- `GOOGLE_CLIENT_ID`, `GOOGLE_SECRET` - Google OAuth
- `LINKEDIN_CLIENT_ID`, `LINKEDIN_SECRET` - LinkedIn OAuth

Set `DEVELOPMENT=True` for local development to disable SSL requirements.

## Notes

- Models use `settings.AUTH_USER_MODEL` for user references
- Navigation is centralized via `home.context_processors.navigation`
- The jobs app has an API endpoint for skills at `jobs:api_skills`
- Job descriptions can be parsed via `jobs:parse_description` endpoint
