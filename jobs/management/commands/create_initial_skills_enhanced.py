from django.core.management.base import BaseCommand
from django.utils.text import slugify
from jobs.models import SkillTreeModel
from jobs.utils.skill_icons import SKILL_ICONS
import logging

logger = logging.getLogger('jobs.skills')

class Command(BaseCommand):
    help = 'Creates and validates initial skills data'

    def handle(self, *args, **kwargs):
        logger.info("Starting skills initialization")
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for icon, name in SKILL_ICONS:
            try:
                skill, created = SkillTreeModel.objects.get_or_create(
                    name=slugify(name),
                    defaults={
                        'label': name,
                        'icon': icon,
                        'tags': slugify(name),
                    }
                )
                
                if created:
                    created_count += 1
                    logger.info(f"Created skill: {name} with icon {icon}")
                else:
                    # Update existing skill if needed
                    if skill.icon != icon or skill.label != name:
                        skill.icon = icon
                        skill.label = name
                        skill.save()
                        updated_count += 1
                        logger.info(f"Updated skill: {name} with new icon {icon}")
                        
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing skill {name}: {str(e)}")

        # Summary
        summary = (
            f"Skills initialization complete.\n"
            f"Created: {created_count}\n"
            f"Updated: {updated_count}\n"
            f"Errors: {error_count}\n"
            f"Total skills: {SkillTreeModel.objects.count()}"
        )
        
        if error_count:
            self.stdout.write(self.style.WARNING(summary))
        else:
            self.stdout.write(self.style.SUCCESS(summary))