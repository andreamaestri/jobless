
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from jobs.models import SkillTreeModel
from jobs.utils.skill_icons import SKILL_ICONS
from jobs.utils.skill_icons import DARK_VARIANTS

class Command(BaseCommand):
    help = 'Populate skills from the shared icon catalogue'

    def handle(self, *args, **kwargs):
        for icon, name in SKILL_ICONS:
            SkillTreeModel.objects.get_or_create(
                name=slugify(name),
                defaults={
                    'label': name,
                    'icon': icon,
                    'tags': slugify(name),
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated skills'))