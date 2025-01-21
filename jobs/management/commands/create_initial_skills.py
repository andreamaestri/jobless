from django.core.management.base import BaseCommand
from jobs.models import SkillsTagModel
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates initial skills data'

    def handle(self, *args, **kwargs):
        initial_skills = [
            {'name': 'python', 'icon': 'logos:python'},
            {'name': 'javascript', 'icon': 'logos:javascript'},
            {'name': 'react', 'icon': 'logos:react'},
            {'name': 'django', 'icon': 'logos:django-icon'},
            {'name': 'aws', 'icon': 'logos:aws'},
            {'name': 'docker', 'icon': 'logos:docker-icon'},
        ]
        
        created_count = 0
        for skill in initial_skills:
            _, created = SkillsTagModel.objects.get_or_create(
                name=skill['name'],
                defaults={'icon': skill['icon']}
            )
            if created:
                created_count += 1
                logger.info(f"Created skill: {skill['name']}")
        
        self.stdout.write(self.style.SUCCESS(
            f'Created {created_count} new skills (total: {SkillsTagModel.objects.count()})'
        ))
