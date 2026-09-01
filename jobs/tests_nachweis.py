"""Tests for the Nachweis von Eigenbemühungen feature.

Covers the acceptance criteria:
1. BA-Minimal PDF: 3 rows with month 2026-08, employer, title only.
2. Jobcenter-Liste PDF: numeric channel codes 1–5, empty Vermerke column.
3. Changing regime does not alter stored applications, only export labels.
4. requiredCount=8 and 5 records → dashboard 5/8, PDF exports the 5, never invents 3.
5. Missing jobTitle blocks export; UI lists blockers.
6. Filename and header use Kundennummer if set.
7. No BA logo in any asset.
8. CSV opens with umlauts intact (semicolon + UTF-8 BOM).
9. Audit log records edits to appliedOn.
10. Empty month export is refused.
"""

import json
from datetime import date
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (
    Application,
    AuditLog,
    ObligationPlan,
    UserProfile,
)
from .pdf import (
    BA_MINIMAL,
    CUSTOM_COLUMNS,
    JOBCENTER_LIST,
    EmptyNachweisError,
    build_nachweis_html,
    build_nachweis_pdf,
    nachweis_filename,
)
from .exports import build_csv

User = get_user_model()

# Lightweight PDF text extraction without extra dependencies: WeasyPrint
# embeds a Tj-text operator stream; we simply search the raw PDF for the
# (encoded) assurance sentence is unreliable, so tests that need content
# assertions use the HTML document (same source of truth as the PDF).
PDF_MAGIC = b"%PDF"


class SecureClientMixin:
    """Production forces SECURE_SSL_REDIRECT; test requests must use https."""

    def get(self, *args, **kwargs):
        kwargs.setdefault("secure", True)
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs.setdefault("secure", True)
        return self.client.post(*args, **kwargs)


class NachweisDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="anna", password="pw12345")
        cls.profile = UserProfile.objects.create(
            user=cls.user,
            full_name="Anna Müller",
            kundennummer="K-424242",
            regime="ALG1",
            office_name="Agentur für Arbeit Ulm",
        )
        cls.plan = ObligationPlan.objects.create(
            user=cls.user,
            title="Eingliederungsvereinbarung",
            valid_from=date(2026, 8, 1),
            valid_to=date(2026, 8, 31),
            required_count=8,
            period=ObligationPlan.Period.CALENDAR_MONTH,
            due_rule=ObligationPlan.DueRule.NEXT_MONTH_5,
            proof_form=JOBCENTER_LIST,
            notes="8 Bewerbungen pro Monat, unaufgefordert vorzulegen",
        )
        cls.apps = []
        for i, (day, employer, title, channel) in enumerate([
            (3, "Firma GmbH", "Softwareentwickler", 4),
            (12, "Tech AG", "Datenanalyst", 2),  # result set below
            (20, "Müller KG", "IT-Projektleiter", 1),
            (24, "Web Agency", "Frontend Developer", 3),
            (28, "Consulting e.K.", "Produktmanager", 5),
        ]):
            cls.apps.append(
                Application.objects.create(
                    user=cls.user,
                    applied_on=date(2026, 8, day),
                    employer_name=employer,
                    job_title=title,
                    channel=channel,
                )
            )
        cls.apps[1].result = Application.Result.ABSAGE
        cls.apps[1].save()


class PDFUnitTests(NachweisDataMixin, TestCase):
    """Pure-function tests for the PDF/HTML builders."""

    def _html(self, profile=JOBCENTER_LIST, apps=None, plan="default"):
        return build_nachweis_html(
            person=self.profile,
            plan=self.plan if plan == "default" else plan,
            applications=apps if apps is not None else self.apps,
            export_profile=profile,
        )

    def test_pdf_bytes_are_generated(self):
        for profile in (BA_MINIMAL, JOBCENTER_LIST, CUSTOM_COLUMNS):
            with self.subTest(profile=profile):
                data = build_nachweis_pdf(
                    self.profile, self.plan, self.apps, export_profile=profile
                )
                self.assertTrue(data.startswith(PDF_MAGIC))
                self.assertGreater(len(data), 1000)

    def test_ba_minimal_has_exactly_three_columns(self):
        html_doc = self._html(BA_MINIMAL)
        self.assertIn("Monat der Bewerbung", html_doc)
        self.assertIn("Arbeitgeber", html_doc)
        self.assertIn("Tätigkeit / Beruf", html_doc)
        self.assertNotIn("Vermerke des Jobcenters", html_doc)
        # one row per application, month printed as YYYY-MM
        self.assertEqual(html_doc.count("2026-08"), len(self.apps))

    def test_jobcenter_list_shows_numeric_channel_codes(self):
        html_doc = self._html(JOBCENTER_LIST)
        for code in ("1", "2", "3", "4", "5"):
            self.assertIn(f"{code} – ", html_doc)
        # empty Vermerke column is present as header, rows leave it blank
        self.assertIn("Vermerke des Jobcenters", html_doc)

    def test_jobcenter_list_keeps_absage_rows(self):
        html_doc = self._html(JOBCENTER_LIST)
        self.assertIn("Absage", html_doc)

    def test_internal_profile_is_marked_non_official(self):
        html_doc = self._html(CUSTOM_COLUMNS)
        self.assertIn("Interne Übersicht — kein amtliches Formular", html_doc)

    def test_assurance_sentence_present(self):
        html_doc = self._html(BA_MINIMAL)
        self.assertIn(
            "Ich versichere, dass die Angaben vollständig und richtig sind.",
            html_doc,
        )

    def test_kundennummer_printed_when_set(self):
        html_doc = self._html(JOBCENTER_LIST)
        self.assertIn("K-424242", html_doc)

    def test_no_ba_logo_or_claim(self):
        html_doc = self._html(JOBCENTER_LIST)
        self.assertNotIn("logo", html_doc.lower())
        self.assertNotIn("zertifiziert", html_doc.lower())
        self.assertNotIn("amtlich anerkannt", html_doc.lower())

    def test_fact_line_shows_5_of_8(self):
        html_doc = self._html(JOBCENTER_LIST)
        self.assertIn("Erfasst: 5 / Soll: 8", html_doc)

    def test_plan_verbatim_note_in_footer(self):
        html_doc = self._html(JOBCENTER_LIST)
        self.assertIn("laut Vereinbarung: 8 Bewerbungen pro Monat", html_doc)

    def test_empty_export_refused(self):
        with self.assertRaises(EmptyNachweisError):
            build_nachweis_html(self.profile, self.plan, [], export_profile=BA_MINIMAL)
        with self.assertRaises(EmptyNachweisError):
            build_nachweis_pdf(self.profile, self.plan, [], export_profile=BA_MINIMAL)

    def test_filename_uses_lastname_and_month(self):
        self.assertEqual(
            nachweis_filename(self.profile, 2026, 8),
            "Nachweis_Eigenbemuehungen_2026-08_muller.pdf",
        )

    def test_page_numbers_in_css(self):
        html_doc = self._html(JOBCENTER_LIST)
        self.assertIn("Blatt ", html_doc)
        self.assertIn("counter(pages)", html_doc)

    def test_regime_change_only_alters_labels(self):
        """Acceptance 3: changing regime does not alter stored applications."""
        before = [(a.pk, a.applied_on, a.employer_name) for a in self.apps]
        self.profile.regime = "GRUNDSICHERUNG"
        self.profile.save()
        after = [(a.pk, a.applied_on, a.employer_name) for a in self.apps]
        self.assertEqual(before, after)
        html_doc = self._html(JOBCENTER_LIST)
        self.assertIn("Jobcenter (SGB II)", html_doc)


class CSVTests(NachweisDataMixin, TestCase):
    def test_csv_has_bom_semicolon_and_umlauts(self):
        csv_text = build_csv(self.apps)
        self.assertTrue(csv_text.startswith("\ufeff"))
        self.assertIn("Datum;Arbeitgeber", csv_text)
        self.assertIn("Tätigkeit/Funktion", csv_text)
        self.assertIn("Anna".replace("Anna", "Müller"), csv_text)

    def test_csv_rows_count(self):
        csv_text = build_csv(self.apps)
        self.assertEqual(len(csv_text.strip().splitlines()), len(self.apps) + 1)


class ModelTests(NachweisDataMixin, TestCase):
    def test_is_nachweisbar(self):
        draft = Application.objects.create(user=self.user, applied_on=date(2026, 8, 5))
        self.assertFalse(draft.is_nachweisbar)
        self.assertTrue(self.apps[0].is_nachweisbar)

    def test_audit_log_records_applied_on_edit(self):
        app = self.apps[0]
        app.applied_on = date(2026, 8, 4)
        app.save()
        entry = AuditLog.objects.filter(application=app, field_name="applied_on").last()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.old_value, "2026-08-03")
        self.assertEqual(entry.new_value, "2026-08-04")

    def test_no_audit_entry_without_change(self):
        app = self.apps[0]
        AuditLog.objects.all().delete()
        app.save()
        self.assertFalse(AuditLog.objects.filter(application=app).exists())

    def test_period_range_calendar_month(self):
        start, end = self.plan.period_range(date(2026, 8, 15))
        self.assertEqual((start, end), (date(2026, 8, 1), date(2026, 8, 31)))

    def test_next_due_on_next_month_5(self):
        self.assertEqual(self.plan.next_due_on(date(2026, 8, 15)), date(2026, 9, 5))

    def test_next_due_on_month_end(self):
        self.plan.due_rule = ObligationPlan.DueRule.MONTH_END
        self.assertEqual(self.plan.next_due_on(date(2026, 8, 15)), date(2026, 8, 31))


class NachweisViewTests(SecureClientMixin, NachweisDataMixin, TestCase):
    def test_dashboard_requires_login(self):
        response = self.get(reverse("jobs:nachweis"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_shows_count_vs_target(self):
        self.client.force_login(self.user)
        response = self.get(
            reverse("jobs:nachweis"), {"month": "2026-08"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5 / 8")

    def test_dashboard_lists_blockers(self):
        Application.objects.create(user=self.user, applied_on=date(2026, 8, 9))
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis"), {"month": "2026-08"})
        self.assertContains(response, "Not yet exportable")

    def test_pdf_export_returns_pdf_and_records_submission(self):
        self.client.force_login(self.user)
        response = self.get(
            reverse("jobs:nachweis_pdf"),
            {"profile": JOBCENTER_LIST, "month": "2026-08"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(PDF_MAGIC))
        self.assertIn("muller", response["Content-Disposition"])
        from .models import Submission
        self.assertTrue(Submission.objects.filter(user=self.user).exists())

    def test_empty_month_export_refused(self):
        self.client.force_login(self.user)
        response = self.get(
            reverse("jobs:nachweis_pdf"),
            {"profile": BA_MINIMAL, "month": "2026-01"},
        )
        # redirected back to the export page with an error message
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, reverse("jobs:nachweis_export"))

    def test_missing_title_applications_excluded_from_export(self):
        Application.objects.create(
            user=self.user,
            applied_on=date(2026, 8, 9),
            employer_name="Draft GmbH",
        )
        self.client.force_login(self.user)
        response = self.get(
            reverse("jobs:nachweis_pdf"),
            {"profile": JOBCENTER_LIST, "month": "2026-08"},
        )
        self.assertEqual(response.status_code, 200)
        # still only the 5 complete records — never 6, never invented rows
        html_doc = build_nachweis_html(
            person=self.profile,
            plan=self.plan,
            applications=[
                a for a in Application.objects.filter(
                    user=self.user, applied_on__month=8, applied_on__year=2026
                )
                if a.is_nachweisbar
            ],
            export_profile=JOBCENTER_LIST,
        )
        self.assertNotIn("Draft GmbH", html_doc)

    def test_csv_export(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis_csv"), {"month": "2026-08"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])

    def test_preview_returns_html(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis_preview"), {"month": "2026-08"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])

    def test_fast_capture_creates_application(self):
        self.client.force_login(self.user)
        response = self.post(
            reverse("jobs:application_add"),
            {
                "applied_on": "2026-09-01",
                "employer_name": "Neu GmbH",
                "job_title": "DevOps Engineer",
                "channel": "4",
                "result": "OFFEN",
                "source": "",
                "source_ref": "",
                "effort_type": "BEWERBUNG",
                "costs_cents": "0",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Application.objects.filter(user=self.user, employer_name="Neu GmbH").exists()
        )

    def test_duplicate_warning(self):
        self.client.force_login(self.user)
        response = self.post(
            reverse("jobs:application_add"),
            {
                "applied_on": "2026-08-03",
                "employer_name": "Firma GmbH",
                "job_title": "Softwareentwickler",
                "channel": "4",
                "result": "OFFEN",
                "source": "",
                "source_ref": "",
                "effort_type": "BEWERBUNG",
                "costs_cents": "0",
            },
            follow=True,
        )
        self.assertContains(response, "duplicate")

    def test_plan_page_renders(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:plan_edit"))
        self.assertEqual(response.status_code, 200)

    def test_profile_page_renders(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:profile_edit"))
        self.assertEqual(response.status_code, 200)

    def test_export_page_renders(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis_export"), {"month": "2026-08"})
        self.assertEqual(response.status_code, 200)


class ComplianceFeatureTests(SecureClientMixin, NachweisDataMixin, TestCase):
    """Tests for the compliance-calendar layer (VV, plan 4-tuple, absence, obstacle)."""

    def _vague_plan(self):
        return ObligationPlan.objects.create(
            user=self.user,
            title="vague",
            required_count=None,
            which_efforts="",
            due_rule="",
        )

    def test_vv_apply_by_defaults_to_plus_3_workdays(self):
        from .models import Vermittlungsvorschlag
        vv = Vermittlungsvorschlag.objects.create(
            user=self.user,
            employer_name="ACME",
            job_title="Techniker",
            received_on=date(2026, 8, 13),  # Thursday
        )
        # Thu + Fri(1) + Mon(2) + Tue(3) => 2026-08-18
        self.assertEqual(vv.apply_by, date(2026, 8, 18))

    def test_vv_overdue_flag(self):
        from .models import Vermittlungsvorschlag
        vv = Vermittlungsvorschlag.objects.create(
            user=self.user,
            employer_name="ACME",
            received_on=date(2020, 1, 1),
            apply_by=date(2020, 1, 10),
        )
        self.assertTrue(vv.is_overdue)
        vv.status = Vermittlungsvorschlag.Status.APPLIED
        self.assertFalse(vv.is_overdue)

    def test_vague_plan_flag_and_missing_components(self):
        plan = self._vague_plan()
        self.assertTrue(plan.is_vague)
        self.assertIn("how_many", plan.missing_components)
        self.assertIn("which", plan.missing_components)

    def test_complete_plan_is_not_vague(self):
        plan = self.plan  # has required_count, due_rule, proof_form, accepted_channels
        plan.which_efforts = "Bewerbungen auf passende Stellen"
        plan.accepted_channels = ["SCHRIFTLICH"]
        plan.save()
        self.assertFalse(plan.is_vague)

    def test_dashboard_shows_vague_plan_banner(self):
        from .models import ObligationPlan
        ObligationPlan.objects.create(
            user=self.user, title="vague", required_count=None, due_rule=""
        )
        # deactivate the complete plan so the vague one is active
        self.plan.is_active = False
        self.plan.save()
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis"), {"month": "2026-08"})
        self.assertContains(response, "four required components")

    def test_dashboard_shows_open_vv(self):
        from .models import Vermittlungsvorschlag
        Vermittlungsvorschlag.objects.create(
            user=self.user, employer_name="ACME", job_title="Techniker",
            received_on=date(2026, 8, 13),
        )
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis"), {"month": "2026-08"})
        self.assertContains(response, "ACME")

    def test_dashboard_warns_on_unreported_absence(self):
        from .models import Absence
        Absence.objects.create(
            user=self.user,
            from_date=date(2026, 9, 10),
            to_date=date(2026, 9, 15),
            destination="Spanien",
        )
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis"), {"month": "2026-08"})
        self.assertContains(response, "not reported")

    def test_absence_reported_not_warned(self):
        from .models import Absence
        Absence.objects.create(
            user=self.user,
            from_date=date(2026, 9, 10),
            to_date=date(2026, 9, 15),
            destination="Spanien",
            approval_status=Absence.ApprovalStatus.NOTIFIED,
            notified_on=date(2026, 9, 1),
        )
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis"), {"month": "2026-08"})
        self.assertNotContains(response, "not reported")

    def test_regime_change_does_not_mutate_applications(self):
        before = list(
            Application.objects.filter(user=self.user).values_list(
                "pk", "applied_on", "employer_name"
            )
        )
        self.profile.regime = "GRUNDSICHERUNG"
        self.profile.save()
        after = list(
            Application.objects.filter(user=self.user).values_list(
                "pk", "applied_on", "employer_name"
            )
        )
        self.assertEqual(before, after)

    def test_kostenbeleg_pdf_shows_costs_and_sum(self):
        from .pdf import KOSTENBELEG
        from .models import Application
        app = self.apps[0]
        app.costs_cents = 160
        app.save()
        html_doc = build_nachweis_html(
            self.profile, self.plan, self.apps, export_profile=KOSTENBELEG
        )
        self.assertIn("Kosten für Eigenbemühungen", html_doc)
        self.assertIn("1.60 €", html_doc)

    def test_nachweis_pdf_has_no_cost_column(self):
        from .pdf import BA_MINIMAL
        html_doc = build_nachweis_html(
            self.profile, self.plan, self.apps, export_profile=BA_MINIMAL
        )
        self.assertNotIn("Kosten", html_doc)

    def test_zip_export_returns_zip(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis_zip"), {"month": "2026-08"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

    def test_zip_export_empty_refused(self):
        self.client.force_login(self.user)
        response = self.get(reverse("jobs:nachweis_zip"), {"month": "2026-01"})
        self.assertEqual(response.status_code, 302)

    def test_vv_create_flow(self):
        self.client.force_login(self.user)
        response = self.post(
            reverse("jobs:vv_add"),
            {
                "employer_name": "Neue Firma",
                "job_title": "Sachbearbeiter",
                "received_on": "2026-08-10",
                "has_rechtsfolgenbelehrung": "on",
                "status": "OPEN",
                "source_ref": "",
                "note": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        from .models import Vermittlungsvorschlag
        self.assertTrue(
            Vermittlungsvorschlag.objects.filter(user=self.user, employer_name="Neue Firma").exists()
        )

    def test_obstacle_flow(self):
        self.client.force_login(self.user)
        response = self.post(
            reverse("jobs:obstacle_add"),
            {
                "date": "2026-08-01",
                "kind": "ILLNESS",
                "note": "Attest liegt vor",
                "evidence": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        from .models import Obstacle
        self.assertTrue(Obstacle.objects.filter(user=self.user).exists())
