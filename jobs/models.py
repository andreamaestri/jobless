from django.db import models
from django.conf import settings
from django.urls import reverse
import tagulous.models


class SkillTreeModel(tagulous.models.TagTreeModel):
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Icon code (e.g., skill-icons:python)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the skill"
    )

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def get_icon(self):
        """Get the icon for this skill"""
        if self.icon:
            return self.icon
        
        # Try ICON_NAME_MAPPING
        from .utils.skill_icons import ICON_NAME_MAPPING
        if self.name in ICON_NAME_MAPPING:
            return ICON_NAME_MAPPING[self.name]
            
        # Log the missing icon mapping
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"No icon found for skill: {self.name}")
        return 'heroicons:academic-cap'  # Default icon


class JobSkill(models.Model):
    PROFICIENCY_LEVELS = [
        ('required', 'Required'),
        ('preferred', 'Preferred'),
        ('bonus', 'Nice to Have')
    ]

    job = models.ForeignKey(
        'JobPosting',
        on_delete=models.CASCADE,
        related_name="job_skills"
    )
    skill = models.ForeignKey(
        SkillTreeModel,
        on_delete=models.CASCADE,
        related_name="job_skills"
    )
    proficiency = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVELS,
        default='required'
    )

    class Meta:
        unique_together = ['job', 'skill']
        verbose_name_plural = "Job Skills"
        indexes = [
            models.Index(fields=['job', 'skill']),
            models.Index(fields=['proficiency']),
        ]

    def __str__(self):
        return (
            f"{self.job.title} - {self.skill.name} "
            f"({self.get_proficiency_display()})"
        )


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
    skills = models.ManyToManyField(
        SkillTreeModel,
        through='JobSkill',
        related_name='jobs',
        help_text="Skills associated with this job posting"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='interested'
    )
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
        return f"{self.user.username}'s favorite: {self.job.title}"

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.job.pk})
