"""CSV / JSON / ZIP exporters for the Nachweis feature."""

import csv
import io
import json
import zipfile

from .pdf import (
    CHANNEL_LABELS_DE,
    RESULT_LABELS_DE,
    EFFORT_LABELS_DE,
    SOURCE_LABELS_DE,
)


CSV_HEADERS = [
    "Datum",
    "Arbeitgeber",
    "Tätigkeit/Funktion",
    "Anschrift",
    "Telefon",
    "E-Mail",
    "Ansprechpartner",
    "Art der Bewerbung",
    "Quelle",
    "Ergebnis",
    "Ergebnisdatum",
    "Bemerkung",
]


def _application_row(app):
    channel = CHANNEL_LABELS_DE.get(int(app.channel), "") if app.channel else ""
    return [
        app.applied_on.isoformat() if app.applied_on else "",
        app.employer_name,
        app.job_title,
        app.employer_address,
        app.employer_phone,
        app.employer_email,
        app.contact_person,
        channel,
        SOURCE_LABELS_DE.get(app.source, app.source or ""),
        RESULT_LABELS_DE.get(app.result, app.result or ""),
        app.result_date.isoformat() if app.result_date else "",
        app.result_note,
    ]


def build_csv(applications):
    """Return a semicolon-delimited CSV with UTF-8 BOM and German headers."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(CSV_HEADERS)
    for app in applications:
        writer.writerow(_application_row(app))
    return "\ufeff" + buffer.getvalue()


def build_json(person, plan, applications):
    """Return a JSON backup of the user's Nachweis data (metadata only)."""
    payload = {
        "profile": {
            "full_name": getattr(person, "full_name", ""),
            "kundennummer": getattr(person, "kundennummer", ""),
            "bg_nummer": getattr(person, "bg_nummer", ""),
            "office_name": getattr(person, "office_name", ""),
            "regime": getattr(person, "regime", ""),
        },
        "plan": {
            "title": plan.title,
            "required_count": plan.required_count,
            "period": plan.period,
            "due_rule": plan.due_rule,
            "proof_form": plan.proof_form,
            "notes": plan.notes,
        } if plan is not None else None,
        "applications": [
            {
                "applied_on": a.applied_on.isoformat() if a.applied_on else None,
                "employer_name": a.employer_name,
                "job_title": a.job_title,
                "employer_address": a.employer_address,
                "employer_phone": a.employer_phone,
                "employer_email": a.employer_email,
                "contact_person": a.contact_person,
                "channel": a.channel,
                "source": a.source,
                "source_ref": a.source_ref,
                "result": a.result,
                "result_date": a.result_date.isoformat() if a.result_date else None,
                "result_note": a.result_note,
                "effort_type": a.effort_type,
                "related_to_vermittlungsvorschlag": a.related_to_vermittlungsvorschlag,
                "costs_cents": a.costs_cents,
            }
            for a in applications
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_zip(pdf_bytes, pdf_name, applications, evidence_mapping):
    """Return a ZIP of the PDF plus selected evidence copies.

    ``evidence_mapping`` maps an application object to a list of
    ``EvidenceFile`` objects (whose ``file`` fields are copied verbatim).
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(pdf_name, pdf_bytes)
        for app, files in evidence_mapping.items():
            for ev in files:
                arcname = f"{app.applied_on:%Y-%m-%d}_{app.employer_name}_"
                arcname += f"{app.job_title}_{ev.filename or ev.file.name}"
                try:
                    zf.write(ev.file.path, arcname=arcname)
                except (ValueError, OSError):
                    continue
    return buffer.getvalue()
