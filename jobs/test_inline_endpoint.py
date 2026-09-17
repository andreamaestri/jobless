from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Application, AuditLog
import datetime

class InlineUpdateTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('inline_user', 'inline@example.com', 'pw')
        self.client.force_login(self.user)
        self.app = Application.objects.create(user=self.user, applied_on=datetime.date(2026,1,1), employer_name='X', job_title='Y')

    def test_inline_update_applied_on_creates_audit(self):
        url = reverse('jobs:application_inline_update', kwargs={'pk': self.app.pk})
        resp = self.client.post(url, {'applied_on': '2026-01-05'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        self.app.refresh_from_db()
        self.assertEqual(str(self.app.applied_on), '2026-01-05')
        al_exists = AuditLog.objects.filter(application=self.app, action='EDIT', field_name='applied_on').exists()
        self.assertTrue(al_exists)
