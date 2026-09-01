import hashlib
import mimetypes
import os
from datetime import date, timedelta

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
import django_tagulous.models


class SkillTag(django_tagulous.models.TagTreeModel):
    class TagMeta:
        force_lowercase = True
        space_delimiter = False
        path_separator = "/"
        autocomplete_view = "jobs:skill_tags_autocomplete"  # Updated to include namespace
        initial = "programming/web, programming/database, programming/mobile"
        protected = False  # Allow tag deletion by default
        case_sensitive = False  # Case-insensitive comparison
        max_count = 10
        use_default_slug = True  # Added for proper slug handling
        
    def __str__(self):
        return self.path


class SkillTreeModel(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Icon code (e.g. skill-icons:python)")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description of the skill")
    )
    tags = django_tagulous.models.TagField(
        to=SkillTag,
        help_text=_("Enter hierarchical tags (e.g. programming/python/django)"),
        blank=True
    )

    @property
    def path(self):
        """Expose a stable path for the skill selector and serializers."""
        return self.name

    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")
        ordering = ['name']

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

    def to_dict(self):
        """Convert skill to dictionary format for JSON serialization"""
        return {
            'id': self.pk,
            'name': self.name,
            'label': self.label,
            'path': self.path,
            'icon': self.get_icon(),
            'description': self.description or '',
            'proficiency_levels': dict(JobSkill.PROFICIENCY_LEVELS)
        }

    def save(self, *args, **kwargs):
        # Ensure name is synced with tags
        if self.name and not self.tags:
            self.tags = self.name
        super().save(*args, **kwargs)

    def clean(self):
        # Ensure name matches the last part of the tag path
        if self.tags:
            tag_parts = str(self.tags).split('/')
            if tag_parts:
                self.name = tag_parts[-1]
        super().clean()


class JobSkill(models.Model):
    PROFICIENCY_LEVELS = [
        ('required', _('Required')),
        ('preferred', _('Preferred')),
        ('bonus', _('Nice to have'))
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
        verbose_name_plural = _("Job skills")
        indexes = [
            models.Index(fields=['job', 'skill']),
            models.Index(fields=['proficiency']),
        ]

    def __str__(self):
        return (
            f"{self.job.title} - {self.skill.name} "
            f"({self.get_proficiency_display()})"
        )

    def to_dict(self):
        """Convert job skill to dictionary format for JSON serialization"""
        return {
            'id': self.pk,
            'skill': self.skill.to_dict(),
            'proficiency': self.proficiency,
            'proficiency_display': self.get_proficiency_display()
        }


class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('interested', _('Interested')),
        ('applied', _('Applied')),
        ('interviewing', _('Interviewing')),
        ('rejected', _('Rejected')),
        ('accepted', _('Accepted'))
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
        help_text=_("Skills linked to this job posting")
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

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.job.pk})


# ---------------------------------------------------------------------------
# Nachweis von Eigenbemühungen (Agentur für Arbeit / Jobcenter)
# ---------------------------------------------------------------------------


class UserProfile(models.Model):
    class Regime(models.TextChoices):
        ALG1 = "ALG1", _("ALG I — Agentur für Arbeit")
        GRUNDSICHERUNG = "GRUNDSICHERUNG", _("Grundsicherung/Bürgergeld — Jobcenter")
        NONE = "NONE", _("None")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="nachweis_profile"
    )
    full_name = models.CharField(_("Full name"), max_length=200, blank=True)
    kundennummer = models.CharField(_("Kundennummer"), max_length=50, blank=True)
    bg_nummer = models.CharField(_("BG-Nummer"), max_length=50, blank=True)
    address = models.TextField(_("Address"), blank=True)
    email = models.EmailField(_("E-mail"), blank=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True)
    regime = models.CharField(
        _("Regime"), max_length=20, choices=Regime.choices, default=Regime.NONE
    )
    office_name = models.CharField(_("Office"), max_length=200, blank=True)
    preferred_locale = models.CharField(
        _("Preferred locale"), max_length=20, default="de-DE"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def __str__(self):
        return self.full_name or self.user.get_username()

    @property
    def last_name(self):
        parts = (self.full_name or "").strip().split()
        return parts[-1] if parts else ""


class ObligationPlan(models.Model):
    class Period(models.TextChoices):
        CALENDAR_MONTH = "CALENDAR_MONTH", _("Calendar month")
        ROLLING_30_DAYS = "ROLLING_30_DAYS", _("Rolling 30 days")
        CUSTOM_RANGE = "CUSTOM_RANGE", _("Custom range")

    class DueRule(models.TextChoices):
        MONTH_END = "MONTH_END", _("Unaufgefordert bis Monatsende")
        NEXT_MONTH_5 = "NEXT_MONTH_5", _("Bis zum 5. des Folgemonats")
        APPOINTMENT = "APPOINTMENT", _("Zum Beratungstermin mitbringen")
        OTHER = "OTHER", _("Sonstiges")

    class ProofForm(models.TextChoices):
        BA_MINIMAL = "BA_MINIMAL", _("BA-Minimal")
        JOBCENTER_LIST = "JOBCENTER_LIST", _("Jobcenter-Liste")
        CUSTOM_COLUMNS = "CUSTOM_COLUMNS", _("Custom columns")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="obligation_plans"
    )
    caseworker = models.ForeignKey(
        "contacts.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="obligation_plans",
        verbose_name=_("Caseworker"),
    )
    title = models.CharField(_("Title"), max_length=200, blank=True)
    valid_from = models.DateField(_("Valid from"), null=True, blank=True)
    valid_to = models.DateField(_("Valid to"), null=True, blank=True)
    required_count = models.PositiveIntegerField(
        _("Required count"), null=True, blank=True
    )
    period = models.CharField(
        _("Period"), max_length=30, choices=Period.choices, default=Period.CALENDAR_MONTH
    )
    due_rule = models.CharField(
        _("Due rule"), max_length=30, choices=DueRule.choices, default=DueRule.MONTH_END
    )
    due_rule_notes = models.CharField(_("Due rule notes"), max_length=200, blank=True)
    accepted_channels = models.JSONField(_("Accepted channels"), default=list, blank=True)
    proof_form = models.CharField(
        _("Proof form"),
        max_length=30,
        choices=ProofForm.choices,
        default=ProofForm.JOBCENTER_LIST,
    )
    notes = models.TextField(_("Notes (verbatim)"), blank=True)
    counts_interviews_as_effort = models.BooleanField(
        _("Interviews count as effort"), default=False
    )
    counts_measures_as_effort = models.BooleanField(
        _("Measures count as effort"), default=False
    )
    counts_jobboard_search_as_effort = models.BooleanField(
        _("Job board search counts as effort"), default=False
    )
    last_submitted_on = models.DateField(_("Last submitted on"), null=True, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-valid_from", "-created_at"]
        verbose_name = _("Obligation plan")
        verbose_name_plural = _("Obligation plans")

    def __str__(self):
        return self.title or _("Obligation plan")

    def period_range(self, reference=None):
        """Return (start, end) dates for this plan's current period."""
        ref = reference or date.today()
        if self.period == self.Period.ROLLING_30_DAYS:
            end = ref
            start = end - timedelta(days=29)
            return start, end
        if self.period == self.Period.CUSTOM_RANGE:
            return (self.valid_from, self.valid_to)
        # CALENDAR_MONTH (default)
        start = ref.replace(day=1)
        if start.month == 12:
            end = date(start.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(start.year, start.month + 1, 1) - timedelta(days=1)
        return start, end

    def next_due_on(self, reference=None):
        """Best-effort next deadline from the due rule, or None."""
        ref = reference or date.today()
        start, end = self.period_range(ref)
        if self.due_rule == self.DueRule.MONTH_END:
            return end
        if self.due_rule == self.DueRule.NEXT_MONTH_5:
            if end.month == 12:
                nxt = date(end.year + 1, 1, 5)
            else:
                nxt = date(end.year, end.month + 1, 5)
            return nxt
        # APPOINTMENT / OTHER cannot be computed here
        return None


class Application(models.Model):
    class Channel(models.IntegerChoices):
        PERSOENLICH = 1, _("In person")
        SCHRIFTLICH = 2, _("Written")
        TELEFONISCH = 3, _("Phone")
        ONLINE = 4, _("Online")
        EMAIL = 5, _("E-mail")

    class Source(models.TextChoices):
        JOBBOERSE_BA = "JOBBOERSE_BA", _("Jobbörse BA")
        STEPSTONE = "STEPSTONE", _("Stepstone")
        LINKEDIN = "LINKEDIN", _("LinkedIn")
        COMPANY_SITE = "COMPANY_SITE", _("Company website")
        NEWSPAPER = "NEWSPAPER", _("Newspaper")
        VERMITTLUNGSVORSCHLAG = "VERMITTLUNGSVORSCHLAG", _("Placement proposal")
        INITIATIVE = "INITIATIVE", _("Initiative")
        OTHER = "OTHER", _("Other")

    class Result(models.TextChoices):
        OFFEN = "OFFEN", _("Open")
        EINGANG_BESTAETIGT = "EINGANG_BESTAETIGT", _("Receipt confirmed")
        GESPRAECH = "GESPRAECH", _("Interview")
        ABSAGE = "ABSAGE", _("Rejected")
        ZUSAGE = "ZUSAGE", _("Accepted")
        ZURUECKGEZOGEN = "ZURUECKGEZOGEN", _("Withdrawn")
        ABGEBROCHEN = "ABGEBROCHEN", _("Aborted")

    class EffortType(models.TextChoices):
        BEWERBUNG = "BEWERBUNG", _("Application")
        INITIATIV = "INITIATIV", _("Initiative application")
        TELEFONAT = "TELEFONAT", _("Phone call")
        VORSPRACHE = "VORSPRACHE", _("Personal visit")
        MASSNAHME = "MASSNAHME", _("Measure")
        JOBBOERSE = "JOBBOERSE", _("Job board search")
        SONSTIGE = "SONSTIGE", _("Other")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    applied_on = models.DateField(_("Applied on"))
    employer_name = models.CharField(_("Employer"), max_length=200, blank=True)
    job_title = models.CharField(_("Job title"), max_length=200, blank=True)
    employer_address = models.CharField(_("Employer address"), max_length=300, blank=True)
    employer_phone = models.CharField(_("Employer phone"), max_length=50, blank=True)
    employer_email = models.EmailField(_("Employer e-mail"), blank=True)
    contact_person = models.CharField(_("Contact person"), max_length=200, blank=True)
    channel = models.IntegerField(
        _("Channel"), choices=Channel.choices, null=True, blank=True
    )
    source = models.CharField(
        _("Source"), max_length=40, choices=Source.choices, blank=True
    )
    source_ref = models.CharField(_("Source reference"), max_length=500, blank=True)
    result = models.CharField(
        _("Result"), max_length=30, choices=Result.choices, default=Result.OFFEN
    )
    result_date = models.DateField(_("Result date"), null=True, blank=True)
    result_note = models.CharField(_("Result note"), max_length=500, blank=True)
    effort_type = models.CharField(
        _("Effort type"),
        max_length=30,
        choices=EffortType.choices,
        default=EffortType.BEWERBUNG,
    )
    related_to_vermittlungsvorschlag = models.BooleanField(
        _("Related to placement proposal"), default=False
    )
    costs_cents = models.PositiveIntegerField(_("Costs (cents)"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_on", "-created_at"]
        verbose_name = _("Job search effort")
        verbose_name_plural = _("Job search efforts")
        indexes = [
            models.Index(fields=["user", "applied_on"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.job_title} — {self.employer_name}"

    @property
    def is_nachweisbar(self):
        return bool(self.applied_on and self.employer_name and self.job_title)

    def save(self, *args, **kwargs):
        is_update = self.pk is not None
        old_applied_on = None
        if is_update:
            old = type(self).objects.filter(pk=self.pk).only("applied_on").first()
            if old is not None:
                old_applied_on = old.applied_on
        super().save(*args, **kwargs)
        if (
            is_update
            and old_applied_on is not None
            and old_applied_on != self.applied_on
        ):
            AuditLog.objects.create(
                user=self.user,
                application=self,
                action="EDIT",
                field_name="applied_on",
                old_value=str(old_applied_on),
                new_value=str(self.applied_on),
            )


class EvidenceFile(models.Model):
    class EvidenceType(models.TextChoices):
        BEWERBUNG = "BEWERBUNG", _("Application copy")
        ABSAGE = "ABSAGE", _("Rejection")
        EINLADUNG = "EINLADUNG", _("Invitation")
        KOSTENBELEG = "KOSTENBELEG", _("Cost receipt")
        KONTOAUSZUG = "KONTOAUSZUG", _("Bank statement")
        SONSTIGES = "SONSTIGES", _("Other")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evidence_files"
    )
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(
        _("File"), upload_to="evidence/%Y/%m", storage=FileSystemStorage(
            location=os.path.join(settings.BASE_DIR, "media", "evidence")
        )
    )
    evidence_type = models.CharField(
        _("Evidence type"),
        max_length=30,
        choices=EvidenceType.choices,
        default=EvidenceType.BEWERBUNG,
    )
    filename = models.CharField(_("Filename"), max_length=300, blank=True)
    mime = models.CharField(_("MIME type"), max_length=100, blank=True)
    size = models.PositiveIntegerField(_("Size"), default=0)
    sha256 = models.CharField(_("SHA-256"), max_length=64, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = _("Evidence file")
        verbose_name_plural = _("Evidence files")

    def __str__(self):
        return self.filename or self.file.name

    def save(self, *args, **kwargs):
        if self.file and not self.sha256:
            try:
                f = self.file.file
                f.seek(0)
                data = f.read()
                self.size = len(data)
                self.sha256 = hashlib.sha256(data).hexdigest()
                self.mime = mimetypes.guess_type(self.file.name)[0] or ""
                self.filename = os.path.basename(self.file.name)
                f.seek(0)
            except (ValueError, OSError):
                pass
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="audit_logs"
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(_("Action"), max_length=40)
    field_name = models.CharField(_("Field"), max_length=100, blank=True)
    old_value = models.TextField(_("Old value"), blank=True)
    new_value = models.TextField(_("New value"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Audit log")
        verbose_name_plural = _("Audit logs")

    def __str__(self):
        return f"{self.action} {self.field_name} @ {self.created_at:%Y-%m-%d %H:%M}"


class Submission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    plan = models.ForeignKey(
        ObligationPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )
    profile = models.CharField(
        _("Export profile"), max_length=30, choices=ObligationPlan.ProofForm.choices
    )
    period_from = models.DateField(_("Period from"))
    period_to = models.DateField(_("Period to"))
    submitted_on = models.DateField(_("Submitted on"), auto_now_add=True)
    rows = models.PositiveIntegerField(_("Rows"), default=0)
    note = models.CharField(_("Note"), max_length=300, blank=True)

    class Meta:
        ordering = ["-submitted_on"]
        verbose_name = _("Submission")
        verbose_name_plural = _("Submissions")

    def __str__(self):
        return f"{self.get_profile_display()} {self.period_from}–{self.period_to}"
