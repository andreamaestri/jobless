from pathlib import Path

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand

from jobs.models import SkillTreeModel


class Command(BaseCommand):
    help = "Synchronize the curated skill taxonomy fixture into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default="jobs/fixtures/initial_skills.yaml",
            help="Fixture path relative to BASE_DIR",
        )

    def handle(self, *args, **options):
        fixture_path = Path(settings.BASE_DIR) / options["fixture"]
        records = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        created = 0
        updated = 0

        for record in records:
            if record.get("model") != "jobs.skilltreemodel":
                continue
            fields = record["fields"]
            skill = (
                SkillTreeModel.objects.filter(name=fields["name"])
                .order_by("pk")
                .first()
            )
            was_created = skill is None
            if was_created:
                skill = SkillTreeModel(name=fields["name"])
            skill.label = fields["label"]
            skill.label_de = fields.get("label_de", "")
            skill.icon = fields.get("icon", "")
            skill.description = fields.get("description", "")
            skill.tags = fields.get("tags", fields["name"])
            skill.dqr_level = fields.get("dqr_level")
            skill.is_mangelberuf = fields.get("is_mangelberuf", False)
            skill.certifications = fields.get("certifications", [])
            skill.save()
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Skill catalog synchronized: {created} created, {updated} updated."
            )
        )
