from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from events.models import Event
from jobs.models import JobPosting
from contacts.models import Contact

User = get_user_model()


class SecureClientMixin:
    """Production forces SECURE_SSL_REDIRECT; test requests must use https."""

    def get(self, *args, **kwargs):
        kwargs.setdefault("secure", True)
        return self.client.get(*args, **kwargs)


class HomeViewTests(SecureClientMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw12345")

    def test_anonymous_redirects_to_login(self):
        response = self.get(reverse("home:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_renders_empty_states(self):
        self.client.force_login(self.user)
        response = self.get(reverse("home:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add contact")
        rows = response.context["status_rows"]
        self.assertEqual(len(rows), len(JobPosting.STATUS_CHOICES))
        self.assertTrue(all(row["count"] == 0 for row in rows))

    def test_dashboard_renders_seeded_data(self):
        job = JobPosting.objects.create(
            user=self.user,
            title="Backend Engineer",
            company="Acme",
            location="Berlin",
            description="Test description",
            status="interviewing",
        )
        Event.objects.create(
            user=self.user,
            title="Final round",
            event_type="interview",
            date=self._days_from_now(2),
            location="Zoom",
        )
        Contact.objects.create(
            user=self.user, name="Maria Rossi", company="Acme", position="Recruiter"
        )

        self.client.force_login(self.user)
        response = self.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend Engineer")
        self.assertContains(response, "Final round")
        self.assertContains(response, "Maria Rossi")
        self.assertContains(response, job.get_status_display())

    def test_status_rows_follow_model_choice_order(self):
        JobPosting.objects.create(
            user=self.user, title="A", company="C", location="L",
            description="d", status="interviewing",
        )
        JobPosting.objects.create(
            user=self.user, title="B", company="C", location="L",
            description="d", status="interested",
        )

        self.client.force_login(self.user)
        response = self.get(reverse("home:home"))

        rows = response.context["status_rows"]
        keys = [row["key"] for row in rows if row["count"]]
        choice_order = [key for key, _ in JobPosting.STATUS_CHOICES]
        self.assertEqual(keys, sorted(keys, key=choice_order.index))

        interviewing = next(r for r in rows if r["key"] == "interviewing")
        self.assertEqual(interviewing["count"], 1)
        self.assertEqual(interviewing["pct"], 50)

    @staticmethod
    def _days_from_now(days):
        from django.utils import timezone
        from datetime import timedelta

        return timezone.now() + timedelta(days=days)
