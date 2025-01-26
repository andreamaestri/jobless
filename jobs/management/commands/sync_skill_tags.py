from django.core.management.base import BaseCommand
from jobs.models import SkillTreeModel


class Command(BaseCommand):
    help = 'Synchronize skill names with their tags'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        updated = 0
        skipped = 0

        self.stdout.write(
            self.style.SUCCESS('Starting tag synchronization...')
        )
        
        skills = SkillTreeModel.objects.all()
        total = skills.count()
        
        if total == 0:
            self.stdout.write(
                self.style.WARNING('No skills found in database')
            )
            return
            
        for skill in skills:
            if skill.name and not skill.tags:
                self.stdout.write(
                    self.style.WARNING(f"Found unsynced skill: {skill.name}")
                )
                if not dry_run:
                    skill.tags = skill.name
                    skill.save()
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Synced tags for '{skill.name}'")
                    )
            else:
                skipped += 1

        summary = []
        if dry_run:
            summary.append("(Dry run - no changes made)")
        
        if updated == 0 and skipped == total:
            summary.append(
                f"✓ All {total} skills are properly synced - "
                f"no changes needed"
            )
        else:
            if updated:
                summary.append(f"Successfully synchronized {updated} skills")
            if skipped:
                summary.append(f"Skipped {skipped} already-synced skills")
                
        self.stdout.write(
            self.style.SUCCESS('\n'.join(summary))
        )
