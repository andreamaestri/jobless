from django.core.management.base import BaseCommand
from jobs.models import SkillsTagModel
from jobs.utils.skill_icons import SKILL_ICONS, DARK_VARIANTS
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates initial skills data'

    def handle(self, *args, **kwargs):
        # Track statistics
        created_count = 0
        updated_count = 0
        error_count = 0

        for icon, name in SKILL_ICONS:
            try:
                # Normalize the name to lowercase
                normalized_name = name.lower()
                
                # Get or create the skill
                skill, created = SkillsTagModel.objects.get_or_create(
                    name=normalized_name,
                    defaults={
                        'icon': icon,
                        'icon_dark': DARK_VARIANTS.get(icon, icon)
                    }
                )

                if created:
                    created_count += 1
                    logger.info(f"Created skill: {normalized_name} with icon {icon}")
                else:
                    # Update existing skill's icons if they've changed
                    if skill.icon != icon or skill.icon_dark != DARK_VARIANTS.get(icon, icon):
                        skill.icon = icon
                        skill.icon_dark = DARK_VARIANTS.get(icon, icon)
                        skill.save()
                        updated_count += 1
                        logger.info(f"Updated skill: {normalized_name} with icon {icon}")

            except Exception as e:
                error_count += 1
                logger.error(f"Error processing skill {name}: {str(e)}")

        # Report results
        self.stdout.write(self.style.SUCCESS(
            f'Skills initialization complete:\n'
            f'- Created: {created_count}\n'
            f'- Updated: {updated_count}\n'
            f'- Errors: {error_count}\n'
            f'- Total skills in database: {SkillsTagModel.objects.count()}'
        ))
