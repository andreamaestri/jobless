from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import JobPosting

User = get_user_model()


class JobModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw12345")
        cls.job = JobPosting.objects.create(
            user=cls.user,
            title="Backend Engineer",
            company="Acme",
            location="Berlin",
            description="Test description",
            status="applied",
        )

    def test_str_returns_title_and_company(self):
        self.assertIn("Backend Engineer", str(self.job))
        self.assertIn("Acme", str(self.job))

    def test_get_absolute_url(self):
        self.assertEqual(self.job.get_absolute_url(), reverse("jobs:detail", kwargs={"pk": self.job.pk}))


class SecureClientMixin:
    """Production forces SECURE_SSL_REDIRECT; test requests must use https."""

    def get(self, *args, **kwargs):
        kwargs.setdefault("secure", True)
        return self.client.get(*args, **kwargs)


class JobViewTests(SecureClientMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw12345")

    def test_list_requires_login(self):
        response = self.get(reverse("jobs:list"))
        self.assertEqual(response.status_code, 302)

    def test_add_requires_login(self):
        response = self.get(reverse("jobs:add"))
        self.assertEqual(response.status_code, 302)

    def test_list_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:list"))
        self.assertEqual(response.status_code, 200)


class JobFilterFavoriteTests(SecureClientMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="filtertester", password="pw12345")
        cls.job = JobPosting.objects.create(
            user=cls.user,
            title="Backend Engineer",
            company="Acme",
            location="Berlin",
            description="desc",
            status="accepted",
        )
        cls.applied_job = JobPosting.objects.create(
            user=cls.user,
            title="Frontend Developer",
            company="Beta",
            location="Remote",
            description="desc",
            status="applied",
        )

    def test_accepted_filter_returns_only_accepted(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:list") + "?filter=accepted")
        self.assertEqual(response.status_code, 200)
        titles = [job.title for job in response.context["jobs"]]
        self.assertIn("Backend Engineer", titles)
        self.assertNotIn("Frontend Developer", titles)

    def test_accepted_filter_button_marked_active(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:list") + "?filter=accepted")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accepted")

    def test_toggle_favorite_returns_json_for_ajax(self):
        self.client.force_login(self.user)
        self.assertFalse(self.job.is_favorited_by(self.user))
        response = self.client.post(
            reverse("jobs:toggle_favorite", kwargs={"pk": self.job.pk}),
            HTTP_HOST="localhost",
            secure=True,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"is_favorite": True})
        self.assertTrue(self.job.is_favorited_by(self.user))

    def test_toggle_favorite_second_call_removes(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("jobs:toggle_favorite", kwargs={"pk": self.job.pk}),
            HTTP_HOST="localhost",
            secure=True,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        response = self.client.post(
            reverse("jobs:toggle_favorite", kwargs={"pk": self.job.pk}),
            HTTP_HOST="localhost",
            secure=True,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"is_favorite": False})

    def test_toggle_favorite_scoped_to_owner(self):
        other = User.objects.create_user(username="intruder", password="pw12345")
        self.client.force_login(other)
        response = self.client.post(
            reverse("jobs:toggle_favorite", kwargs={"pk": self.job.pk}),
            HTTP_HOST="localhost",
            secure=True,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 404)

    def test_favorites_filter_returns_only_favorited(self):
        self.job.toggle_favorite(self.user)
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:list") + "?filter=favorites")
        self.assertEqual(response.status_code, 200)
        titles = [job.title for job in response.context["jobs"]]
        self.assertIn("Backend Engineer", titles)
        self.assertNotIn("Frontend Developer", titles)
