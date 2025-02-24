# Generated by Django 5.1.4 on 2025-01-26 16:16

import django.db.models.deletion
import tagulous.models.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="JobFavorite",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_favorites",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="JobPosting",
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
                ("company", models.CharField(max_length=200)),
                ("location", models.CharField(max_length=200)),
                ("salary_range", models.CharField(blank=True, max_length=100)),
                ("url", models.URLField(blank=True)),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("interested", "Interested"),
                            ("applied", "Applied"),
                            ("interviewing", "Interviewing"),
                            ("rejected", "Rejected"),
                            ("accepted", "Accepted"),
                        ],
                        default="interested",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "favorites",
                    models.ManyToManyField(
                        blank=True,
                        related_name="favorited_jobs",
                        through="jobs.JobFavorite",
                        to=settings.AUTH_USER_MODEL,
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
                "ordering": ["-updated_at"],
            },
        ),
        migrations.AddField(
            model_name="jobfavorite",
            name="job",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites_set",
                to="jobs.jobposting",
            ),
        ),
        migrations.CreateModel(
            name="SkillTreeModel",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField()),
                (
                    "count",
                    models.IntegerField(
                        default=0,
                        help_text="Internal counter of how many times this tag is in use",
                    ),
                ),
                (
                    "protected",
                    models.BooleanField(
                        default=False,
                        help_text="Will not be deleted when the count reaches 0",
                    ),
                ),
                ("path", models.TextField()),
                (
                    "level",
                    models.IntegerField(
                        default=1, help_text="The level of the tag in the tree"
                    ),
                ),
                ("label", models.CharField(max_length=100)),
                (
                    "icon",
                    models.CharField(
                        blank=True,
                        help_text="Icon code (e.g., skill-icons:python)",
                        max_length=100,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Detailed description of the skill"
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="jobs.skilltreemodel",
                    ),
                ),
            ],
            options={
                "verbose_name": "Skill",
                "verbose_name_plural": "Skills",
                "ordering": ["name"],
            },
            bases=(tagulous.models.models.BaseTagTreeModel, models.Model),
        ),
        migrations.CreateModel(
            name="JobSkill",
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
                (
                    "proficiency",
                    models.CharField(
                        choices=[
                            ("required", "Required"),
                            ("preferred", "Preferred"),
                            ("bonus", "Nice to Have"),
                        ],
                        default="required",
                        max_length=20,
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_skills",
                        to="jobs.jobposting",
                    ),
                ),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_skills",
                        to="jobs.skilltreemodel",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Job Skills",
            },
        ),
        migrations.AddField(
            model_name="jobposting",
            name="skills",
            field=models.ManyToManyField(
                help_text="Skills associated with this job posting",
                related_name="jobs",
                through="jobs.JobSkill",
                to="jobs.skilltreemodel",
            ),
        ),
        migrations.AddIndex(
            model_name="jobfavorite",
            index=models.Index(
                fields=["user", "job"], name="jobs_jobfav_user_id_9fabd7_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="jobfavorite",
            index=models.Index(
                fields=["created_at"], name="jobs_jobfav_created_e2456f_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="jobfavorite",
            unique_together={("user", "job")},
        ),
        migrations.AddIndex(
            model_name="jobskill",
            index=models.Index(
                fields=["job", "skill"], name="jobs_jobski_job_id_2a5c45_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="jobskill",
            index=models.Index(
                fields=["proficiency"], name="jobs_jobski_profici_81d66d_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="jobskill",
            unique_together={("job", "skill")},
        ),
        migrations.AddIndex(
            model_name="jobposting",
            index=models.Index(
                fields=["-created_at"], name="jobs_jobpos_created_ba4c9f_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="jobposting",
            index=models.Index(fields=["status"], name="jobs_jobpos_status_99cc43_idx"),
        ),
        migrations.AddIndex(
            model_name="jobposting",
            index=models.Index(fields=["user"], name="jobs_jobpos_user_id_834724_idx"),
        ),
    ]
