"""Pure PDF generation for the "Nachweis von Eigenbemühungen".

The public entry point :func:`build_nachweis_pdf` is a pure function of its
inputs (person, plan, applications) and returns ``bytes`` so it can be
unit-tested without a request or database.

Official labels are hardcoded German strings on purpose: they must remain German
even when the surrounding UI is switched to another language.
"""

import html
import os
from datetime import date

from django.conf import settings
from django.utils.text import slugify

from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration


class EmptyNachweisError(Exception):
    """Raised when an export would produce a PDF with zero rows."""


# Export profile constants (mirror ObligationPlan.ProofForm values).
BA_MINIMAL = "BA_MINIMAL"
JOBCENTER_LIST = "JOBCENTER_LIST"
CUSTOM_COLUMNS = "CUSTOM_COLUMNS"

# German labels for the official forms (never translated away).
CHANNEL_LABELS_DE = {
    1: "persönlich",
    2: "schriftlich",
    3: "telefonisch",
    4: "online",
    5: "E-Mail",
}

RESULT_LABELS_DE = {
    "OFFEN": "offen",
    "EINGANG_BESTAETIGT": "Eingang bestätigt",
    "GESPRAECH": "Gespräch",
    "ABSAGE": "Absage",
    "ZUSAGE": "Zusage",
    "ZURUECKGEZOGEN": "zurückgezogen",
    "ABGEBROCHEN": "abgebrochen",
}

EFFORT_LABELS_DE = {
    "BEWERBUNG": "Bewerbung",
    "INITIATIV": "Initiativbewerbung",
    "TELEFONAT": "Telefonat",
    "VORSPRACHE": "Vorsprache",
    "MASSNAHME": "Maßnahme",
    "JOBBOERSE": "Jobbörse",
    "SONSTIGE": "Sonstiges",
}

SOURCE_LABELS_DE = {
    "JOBBOERSE_BA": "Jobbörse BA",
    "STEPSTONE": "Stepstone",
    "LINKEDIN": "LinkedIn",
    "COMPANY_SITE": "Firmenwebsite",
    "NEWSPAPER": "Zeitung",
    "VERMITTLUNGSVORSCHLAG": "Vermittlungsvorschlag",
    "INITIATIVE": "Initiativ",
    "OTHER": "Sonstiges",
}

REGIME_LABELS_DE = {
    "ALG1": "Agentur für Arbeit (SGB III)",
    "GRUNDSICHERUNG": "Jobcenter (SGB II)",
    "NONE": "",
}

TITLE = "Nachweis von Eigenbemühungen"
ASSURANCE = "Ich versichere, dass die Angaben vollständig und richtig sind."


def _font_path():
    return os.path.join(settings.BASE_DIR, "static", "fonts", "din1451alt.ttf")


def _esc(value):
    if value is None:
        return ""
    return html.escape(str(value))


def _month(value):
    return value.strftime("%Y-%m") if isinstance(value, date) else str(value)


def _day(value):
    return value.strftime("%d.%m.%Y") if isinstance(value, date) else str(value)


def _channel_display(channel):
    if channel is None:
        return ""
    label = CHANNEL_LABELS_DE.get(int(channel), "")
    return f"{channel} – {label}" if label else str(channel)


def _base_css(font_url):
    css = """
    @page {
      size: A4 portrait;
      margin: 2cm 1.6cm 2.2cm 1.6cm;
      @bottom-center {
        content: "Blatt " counter(page) " von " counter(pages);
        font-family: "DIN1451", "Noto Sans", sans-serif;
        font-size: 8pt;
        color: #000;
      }
    }
    @font-face {
      font-family: "DIN1451";
      src: url("__FONT_URL__") format("truetype");
      font-weight: normal;
      font-style: normal;
    }
    body {
      font-family: "DIN1451", "Noto Sans", sans-serif;
      font-size: 10pt;
      color: #000;
      line-height: 1.35;
    }
    h1 {
      font-size: 14pt;
      text-align: center;
      margin: 0 0 6pt 0;
    }
    .subtitle {
      text-align: center;
      font-size: 9pt;
      margin: 0 0 10pt 0;
    }
    table.meta {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 10pt;
    }
    table.meta td {
      padding: 1pt 4pt;
      vertical-align: top;
      font-size: 10pt;
    }
    table.data {
      width: 100%;
      border-collapse: collapse;
    }
    table.data th, table.data td {
      border: 0.6pt solid #000;
      padding: 3pt 4pt;
      vertical-align: top;
      text-align: left;
      font-size: 9.5pt;
    }
    table.data th {
      font-weight: bold;
    }
    .footer {
      margin-top: 14pt;
    }
    .signature {
      margin-top: 30pt;
    }
    .signature .line {
      display: inline-block;
      width: 45%;
    }
    .factline {
      margin-top: 8pt;
      font-size: 9pt;
    }
    .notice {
      margin-top: 8pt;
      font-size: 8.5pt;
    }
    """
    return css.replace("__FONT_URL__", font_url)


def _header_html(person):
    rows = []
    if getattr(person, "full_name", ""):
        rows.append(("Name", person.full_name))
    if getattr(person, "kundennummer", ""):
        rows.append(("Kundennummer", person.kundennummer))
    if getattr(person, "bg_nummer", ""):
        rows.append(("BG-Nummer", person.bg_nummer))
    if getattr(person, "office_name", ""):
        rows.append(("Dienststelle", person.office_name))
    regime = REGIME_LABELS_DE.get(getattr(person, "regime", "NONE"), "")
    if regime:
        rows.append(("Rechtskreis", regime))
    return "".join(
        f'<td><strong>{_esc(k)}:</strong></td><td>{_esc(v)}</td>' for k, v in rows
    )


def _signature_html():
    return (
        '<div class="signature">'
        '<span class="line">____________________________________</span>'
        '&nbsp;&nbsp;&nbsp;&nbsp;'
        '<span class="line">____________________________________</span>'
        '<br/><span class="line">Ort, Datum</span>'
        '&nbsp;&nbsp;&nbsp;&nbsp;'
        '<span class="line">Unterschrift</span>'
        "</div>"
    )


def _assurance_html():
    return f'<div class="notice"><strong>{ASSURANCE}</strong></div>'


def _plan_footer_html(plan, count):
    parts = []
    if plan is not None and getattr(plan, "notes", ""):
        parts.append(f"laut Vereinbarung: {_esc(plan.notes)}")
    if plan is not None and plan.required_count is not None:
        parts.append(f"Erfasst: {count} / Soll: {plan.required_count}")
    return "".join(f'<div class="notice">{p}</div>' for p in parts)


def _profile_a_html(person, applications, plan=None):
    rows = "".join(
        "<tr>"
        f"<td>{_month(a.applied_on)}</td>"
        f"<td>{_esc(a.employer_name)}</td>"
        f"<td>{_esc(a.job_title)}</td>"
        "</tr>"
        for a in applications
    )
    return f"""
    <h1>{TITLE}</h1>
    <table class="meta"><tr>{_header_html(person)}</tr></table>
    <table class="data">
      <thead><tr>
        <th>Monat der Bewerbung</th>
        <th>Arbeitgeber</th>
        <th>Tätigkeit / Beruf</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    {_signature_html()}
    {_assurance_html()}
    """


def _profile_b_html(person, applications, plan=None):
    rows = "".join(
        "<tr>"
        f"<td>{_day(a.applied_on)}</td>"
        f"<td>{_esc(a.employer_name)}<br/>"
        f'<span style="font-size:8pt;">{_esc(a.employer_address)}'
        f"{', ' if a.employer_address and a.employer_phone else ''}"
        f"{_esc(a.employer_phone)}</span></td>"
        f"<td>{_esc(a.contact_person)}</td>"
        f"<td>{_esc(a.job_title)}</td>"
        f"<td>{_channel_display(a.channel)}</td>"
        f"<td>{_esc(RESULT_LABELS_DE.get(a.result, a.result))}</td>"
        f"<td></td>"
        "</tr>"
        for a in applications
    )
    footer = f"""
    <div class="footer">
      <div>Anzahl der Bewerbungen: {len(applications)}</div>
      {_plan_footer_html(plan, len(applications))}
    </div>
    {_signature_html()}
    {_assurance_html()}
    """
    return f"""
    <h1>{TITLE}</h1>
    <table class="meta"><tr>{_header_html(person)}</tr></table>
    <table class="data">
      <thead><tr>
        <th>Datum</th>
        <th>Firma (Anschrift, Telefon)</th>
        <th>Ansprechpartner</th>
        <th>Tätigkeit/Funktion</th>
        <th>Art der Bewerbung<br/><span style="font-size:7.5pt;">1 persönlich / 2 schriftlich / 3 telefonisch / 4 online / 5 E-Mail</span></th>
        <th>Ergebnis</th>
        <th>Vermerke des Jobcenters</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    {footer}
    """


def _profile_c_html(person, applications, plan=None):
    rows = "".join(
        "<tr>"
        f"<td>{_day(a.applied_on)}</td>"
        f"<td>{_esc(a.employer_name)}</td>"
        f"<td>{_esc(a.job_title)}</td>"
        f"<td>{_esc(EFFORT_LABELS_DE.get(a.effort_type, a.effort_type))}</td>"
        f"<td>{_esc(SOURCE_LABELS_DE.get(a.source, a.source))}</td>"
        f"<td>{_esc(RESULT_LABELS_DE.get(a.result, a.result))}</td>"
        "</tr>"
        for a in applications
    )
    return f"""
    <h1>{TITLE}</h1>
    <div class="subtitle">Interne Übersicht — kein amtliches Formular</div>
    <table class="meta"><tr>{_header_html(person)}</tr></table>
    <table class="data">
      <thead><tr>
        <th>Datum</th>
        <th>Arbeitgeber</th>
        <th>Tätigkeit / Beruf</th>
        <th>Bewerbungsweg</th>
        <th>Quelle</th>
        <th>Status</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


_BUILDERS = {
    BA_MINIMAL: _profile_a_html,
    JOBCENTER_LIST: _profile_b_html,
    CUSTOM_COLUMNS: _profile_c_html,
}


def build_nachweis_html(person, plan, applications, export_profile=JOBCENTER_LIST,
                        font_path=None):
    """Return the full standalone HTML document (used for preview and PDF).

    ``applications`` is a list/queryset of :class:`~jobs.models.Application`.
    ``person`` is a :class:`~jobs.models.UserProfile` (or any object exposing
    ``full_name``, ``kundennummer``, ``bg_nummer``, ``office_name`` and
    ``regime``). ``plan`` is an :class:`~jobs.models.ObligationPlan` or ``None``.
    """
    applications = list(applications)
    if not applications:
        raise EmptyNachweisError("Keine nachweisbaren Bewerbungen im gewählten Zeitraum.")

    builder = _BUILDERS.get(export_profile, _profile_b_html)
    body_html = builder(person, applications, plan)

    font_url = "file://" + (font_path or _font_path())
    css = _base_css(font_url)
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{css}</style></head><body>{body_html}</body></html>"
    )


def build_nachweis_pdf(person, plan, applications, export_profile=JOBCENTER_LIST,
                       font_path=None):
    """Return the PDF as ``bytes``. See :func:`build_nachweis_html`."""
    document = HTML(string=build_nachweis_html(
        person, plan, applications, export_profile, font_path
    ))
    return document.write_pdf(font_config=FontConfiguration())


def nachweis_filename(person, year, month):
    """Return ``Nachweis_Eigenbemuehungen_YYYY-MM_Nachname.pdf``."""
    last_name = ""
    if person is not None:
        last_name = slugify(getattr(person, "last_name", "") or "") or "Nachname"
    return f"Nachweis_Eigenbemuehungen_{year:04d}-{month:02d}_{last_name}.pdf"
