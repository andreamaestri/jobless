from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Contact

User = get_user_model()


class ContactModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw12345")
        cls.contact = Contact.objects.create(
            user=cls.user, name="Maria Rossi", company="Acme", position="Recruiter"
        )

    def test_str_returns_name(self):
        self.assertIn("Maria Rossi", str(self.contact))

    def test_get_absolute_url(self):
        self.assertEqual(
            self.contact.get_absolute_url(),
            reverse("contacts:detail", kwargs={"pk": self.contact.pk}),
        )


class SecureClientMixin:
    """Production forces SECURE_SSL_REDIRECT; test requests must use https."""

    def get(self, *args, **kwargs):
        kwargs.setdefault("secure", True)
        return self.client.get(*args, **kwargs)


class ContactViewTests(SecureClientMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw12345")

    def test_list_requires_login(self):
        response = self.get(reverse("contacts:list"))
        self.assertEqual(response.status_code, 302)

    def test_list_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.get(reverse("contacts:list"))
        self.assertEqual(response.status_code, 200)
