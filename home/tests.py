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


class SearchApiTests(SecureClientMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="searcher", password="pw12345")
        cls.other = User.objects.create_user(username="other", password="pw12345")
        cls.job = JobPosting.objects.create(
            user=cls.user,
            title="Python Developer",
            company="Acme GmbH",
            location="Berlin",
            description="Build things",
            status="interested",
        )
        cls.event = Event.objects.create(
            user=cls.user,
            title="Team Meeting",
            event_type="meeting",
            date=cls._days_from_now(1),
            location="Office",
        )
        cls.contact = Contact.objects.create(
            user=cls.user, name="Maria Rossi", company="Acme GmbH", email="maria@example.com"
        )
        cls.other_job = JobPosting.objects.create(
            user=cls.other,
            title="Python Guru",
            company="Competitor",
            location="Remote",
            description="",
            status="interested",
        )

    def test_anonymous_redirects_to_login(self):
        response = self.get(reverse("home:api_search") + "?q=python")
        self.assertIn(response.status_code, (302, 401))

    def test_blank_query_returns_empty_list(self):
        self.client.force_login(self.user)
        response = self.get(reverse("home:api_search") + "?q=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_short_query_returns_empty_list(self):
        self.client.force_login(self.user)
        response = self.get(reverse("home:api_search") + "?q=x")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_results_scoped_to_current_user(self):
        self.client.force_login(self.user)
        response = self.get(reverse("home:api_search") + "?q=python")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        titles = [item["title"] for item in data]
        self.assertIn("Python Developer", titles)
        self.assertNotIn("Python Guru", titles)

    def test_results_capped_at_eight(self):
        for i in range(10):
            JobPosting.objects.create(
                user=self.user,
                title=f"Role {i}",
                company="Acme",
                location="Berlin",
                description="",
                status="interested",
            )
        self.client.force_login(self.user)
        response = self.get(reverse("home:api_search") + "?q=role")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.json()), 8)

    def test_result_structure(self):
        self.client.force_login(self.user)
        response = self.get(reverse("home:api_search") + "?q=maria")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)
        item = data[0]
        self.assertEqual(set(item.keys()), {"icon", "title", "subtitle", "url"})
        self.assertTrue(item["url"].startswith("/"))

    @staticmethod
    def _days_from_now(days):
        from django.utils import timezone
        from datetime import timedelta

        return timezone.now() + timedelta(days=days)
