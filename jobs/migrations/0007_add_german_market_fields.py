from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_application_job_posting_applicationtag_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='skilltreemodel',
            name='label_de',
            field=models.CharField(
                blank=True,
                default='',
                help_text='German display name (e.g. SPS-Programmierung)',
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name='skilltreemodel',
            name='dqr_level',
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text='DQR/EQF qualification level (1–8)',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='skilltreemodel',
            name='is_mangelberuf',
            field=models.BooleanField(
                default=False,
                help_text='Official BA Engpassberuf (shortage occupation)',
            ),
        ),
        migrations.AddField(
            model_name='skilltreemodel',
            name='certifications',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of certification names (e.g. ["PersCert TÜV", "Siemens Certified"])',
            ),
        ),
    ]
