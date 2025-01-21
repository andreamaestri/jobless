from django.db import models
from django.conf import settings
from django.urls import reverse
from tagulous.models import TagField
from django.contrib.auth.models import User
import tagulous.models
from .utils.skill_icons import SKILL_ICONS, DARK_VARIANTS
from django.contrib.auth import get_user_model

class SkillsTagModel(tagulous.models.TagModel):
    icon = models.CharField(max_length=100, blank=True, null=True)
    icon_dark = models.CharField(max_length=100, blank=True, null=True)
    
    class TagMeta:
        initial = SKILL_ICONS
        force_lowercase = True
        autocomplete_view = 'jobs:skills_autocomplete'
        space_delimiter = False
        max_count = 10
        case_sensitive = False

    def get_icon(self):
        """Get the icon for this skill"""
        if self.icon:
            return self.icon
        # Fallback to default mapping
        for icon, name in SKILL_ICONS:
            if name.lower() == str(self).lower():
                return icon
        return 'heroicons:academic-cap'  # Default icon

    def get_icon_dark(self):
        """Get the dark mode icon for this skill"""
        if self.icon_dark:
            return self.icon_dark
        # Fallback to default mapping
        icon = self.get_icon()
        return DARK_VARIANTS.get(icon, icon)

    def __str__(self):
        return f"{self.name} ({self.icon})"

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('interested', 'Interested'),
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    salary_range = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    description = models.TextField()
    skills = tagulous.models.TagField(
        to=SkillsTagModel,
        help_text="Select skills from the predefined list",
        blank=True,
        related_name="job_skills"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='interested')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favorite = models.ManyToManyField(User, related_name="favourited_jobs", blank=True)
    favorites = models.ManyToManyField(
        get_user_model(),
        related_name='favorite_jobs',
        blank=True,
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})
