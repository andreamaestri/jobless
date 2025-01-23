from django.core.management.base import BaseCommand
from django.db.models import Count
from jobs.models import SkillsTagModel
from jobs.utils.skill_icons import SKILL_ICONS, DARK_VARIANTS
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Validate and report skills data status'

    def handle(self, *args, **kwargs):
        # Check existing skills
        existing_skills = SkillsTagModel.objects.all()
        self.stdout.write(f"Found {existing_skills.count()} skills in database")

        # Validate icons
        for skill in existing_skills:
            if not skill.icon:
                logger.warning(f"Skill '{skill.name}' has no icon")
            elif skill.icon not in DARK_VARIANTS:
                logger.warning(f"Skill '{skill.name}' has icon '{skill.icon}' with no dark variant")

        # Check for duplicates
        duplicate_names = (SkillsTagModel.objects.values('name')
                        .annotate(name_count=Count('id'))
                        .filter(name_count__gt=1))
        if duplicate_names.exists():
            logger.error(f"Found duplicate skills: {list(duplicate_names)}")
            
        # Verify all required skills exist
        db_skills = set(existing_skills.values_list('name', flat=True))
        icon_skills = set(name.lower() for _, name in SKILL_ICONS)
        missing = icon_skills - db_skills
        if missing:
            logger.warning(f"Missing skills: {missing}")

        # Output summary
        self.stdout.write(self.style.SUCCESS(
            f'Validation complete. Found {existing_skills.count()} skills, '
            f'{len(missing)} missing, {duplicate_names.count()} duplicates'
        ))