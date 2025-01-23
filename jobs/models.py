from django.db import models
from django.conf import settings
from django.urls import reverse
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
        # First try ICON_NAME_MAPPING
        skill_name = str(self).lower()
        from .utils.skill_icons import ICON_NAME_MAPPING
        if skill_name in ICON_NAME_MAPPING:
            return ICON_NAME_MAPPING[skill_name]
            
        # Then try SKILL_ICONS
        for icon, name in SKILL_ICONS:
            if name.lower() == skill_name:
                return icon
                
        # Log the missing icon mapping
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"No icon found for skill: {str(self)}")
        return 'heroicons:academic-cap'  # Default icon

    def get_icon_dark(self):
        """Get the dark mode icon for this skill"""
        if self.icon_dark:
            return self.icon_dark
        # Fallback to default mapping
        icon = self.get_icon()
        return DARK_VARIANTS.get(icon, icon)

    def __str__(self):
        return self.name

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
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='JobFavorite',
        related_name='favorited_jobs',
        blank=True
    )

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})

    @property
    def favorite_count(self):
        """Get the number of users who favorited this job"""
        return self.favorites.count()

    def is_favorited_by(self, user):
        """Check if job is favorited by user"""
        if not user.is_authenticated:
            return False
        return self.jobfavorite_set.filter(user=user).exists()

    def toggle_favorite(self, user):
        """Toggle favorite status for user"""
        if not user.is_authenticated:
            return False
        favorite, created = self.jobfavorite_set.get_or_create(user=user)
        if not created:
            favorite.delete()
        return created

class JobFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_favorites'
    )
    job = models.ForeignKey(
        'JobPosting',
        on_delete=models.CASCADE,
        related_name='favorites_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'job']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.job.title}"

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.job.pk})
