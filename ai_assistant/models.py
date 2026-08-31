from django.conf import settings
from django.db import models


class UserCV(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cv',
    )
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User CV'
        verbose_name_plural = 'User CVs'

    def __str__(self):
        return f"CV of {self.user}"


class AssistantRun(models.Model):
    KIND_CHOICES = [
        ('feedback', 'CV Feedback'),
        ('cover_letter', 'Cover Letter'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assistant_runs',
    )
    job = models.ForeignKey(
        'jobs.JobPosting',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assistant_runs',
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Assistant runs'

    def __str__(self):
        return f"{self.get_kind_display()} by {self.user}"
