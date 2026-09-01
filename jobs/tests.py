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
