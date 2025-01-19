
from django.core.management.base import BaseCommand
from jobs.models import Skill
from jobs.models import SKILL_ICONS
from jobs.utils.skill_icons import DARK_VARIANTS

class Command(BaseCommand):
    help = 'Populate skills from SKILL_ICONS'

    def handle(self, *args, **kwargs):
        for icon, name in SKILL_ICONS:
            Skill.objects.get_or_create(
                name=name,
                defaults={
                    'icon': icon,
                    'icon_dark': DARK_VARIANTS.get(icon, icon)
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully populated skills'))