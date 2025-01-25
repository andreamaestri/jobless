# Generated by Django 5.1.4 on 2025-01-25 20:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contacts", "0001_initial"),
        ("jobs", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("interview", "Interview"),
                            ("meeting", "Meeting"),
                            ("followup", "Follow-up"),
                            ("networking", "Networking Event"),
                        ],
                        max_length=20,
                    ),
                ),
                ("date", models.DateTimeField()),
                ("location", models.CharField(max_length=200)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "contacts",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="contacts.contact",
                    ),
                ),
                (
                    "job_posting",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="jobs.jobposting",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["date"],
            },
        ),
    ]
