# AGENTS.md

Project-specific instructions for coding agents working on **Jobless** — a Django 5.1
job-search tracker (jobs, contacts, events, AI assistant) with a daisyUI 5 + Tailwind 4
frontend. Complements `README.md`, the more detailed `CLAUDE.md`, and `docs/architecture/`.

## Setup

- Python venv: `.venv/` — run everything as `.venv/bin/python manage.py ...`.
- Production env lives in root-owned `/etc/jobless.env` (DB creds included). Without it,
  DB access fails with `fe_sendauth: no password supplied`. Load it:
  `sudo bash -c 'set -a; source /etc/jobless.env; ...'`. Repo `.env` is for local dev.
- Node >= 22 required (`package.json` engines). `npm install` at root (Vite/Alpine) and
  `python manage.py tailwind install` for `theme/static_src`.

## Commands

- Check: `.venv/bin/python manage.py check`; tests: `.venv/bin/python manage.py test jobs`
  (also `contacts`, `events`). Always pass `--noinput` (leftover test DBs otherwise prompt
  and hang non-interactive runs). The DB role needs `CREATEDB` (granted via
  `sudo -u postgres psql -c 'ALTER ROLE jobless CREATEDB;'`). Tests must issue https
  requests (`secure=True`): production redirects http. In Django 6.1 `secure` is a
  per-request kwarg — `Client(secure=True)` is silently ignored (goes into `**defaults`);
  see the `SecureClientMixin` in the app `tests.py` files.
- Frontend assets, in this order after template/CSS changes:
  1. `python manage.py tailwind build` (runs npm inside `theme/static_src`, writes
     `theme/static/css/dist/styles.css`)
  2. `sudo chown -R $(whoami): staticfiles` (often root-owned), then
     `python manage.py collectstatic --noinput`
  3. `sudo systemctl restart jobless` (systemd, Gunicorn on `127.0.0.1:8001`)
- i18n (German only): `makemessages -l de` — never use `--no-location` (strips all
  `#:` comments and bloats the diff). Compile just the project catalog with
  `compilemessages --locale=de` (bare `compilemessages` walks every installed app and is
  slow). Validate with `msgfmt --check-format locale/de/LC_MESSAGES/django.po`.
  When hand-editing `.po`, remove `#, fuzzy` and `#|` lines; verify escapes in `msgstr`
  (a script-written `\\"` double-escape renders literally).

## Verifying live pages

- Use a Django test client against the running config:
  `Client(SERVER_NAME="localhost")`, `force_login(user)`,
  `c.get(url, HTTP_HOST="localhost", secure=True)` — `secure=True` is required.
- To render pages with data without touching prod data, seed inside
  `transaction.atomic()` and call `transaction.set_rollback(True)` before exiting.
- Useful URLs: `/`, `/jobs/`, `/jobs/add/`, `/events/`, `/contacts/`, `/ai-assistant/`,
  `/jsi18n/` (JS catalog).

## Conventions

- Tailwind 4 is CSS-first: themes and plugins live in `theme/static_src/src/styles.css`
  via `@plugin 'daisyui/theme'` blocks (Jobless/Dark). All `tailwind.config.js` files are
  ignored/unwired — do not add config there.
- daisyUI 5 only: use semantic colors (`bg-base-100`, `text-base-content`) and v5 classes
  (`fieldset`, `join`, `tabs-box`, `<dialog class="modal">` + `modal-box` +
  `form.modal-backdrop`). Never put `@apply` in template `<style>` blocks — it is not
  processed there; put styles in `styles.css`.
- i18n: English is the source language. Wrap user-facing strings (`{% translate %}`,
  `gettext_lazy`; model choices included) and add German `msgstr` to
  `locale/de/LC_MESSAGES/django.po` (JS labels go in `djangojs.po` — note literals inside
  inline `<script>` blocks stay English).
- URLs are namespaced (`jobs:list`, `contacts:detail`, ...); reference by name in templates.
- Models reference users via `settings.AUTH_USER_MODEL`.

## Git quirks

- `theme/static/css/dist/styles.css` is tracked but matched by `.gitignore`'s `dist` rule —
  stage it with `git add -f`.
- Never commit `staticfiles/` artifacts.

## Code Review Rules

- Flag daisyUI 4-era classes (`form-control`, `input-bordered`, `select-bordered`,
  `btn-primary-focus`, `tabs-boxed`, `input-group`) — replace with v5 equivalents.
- Flag hardcoded palette classes (`bg-green-100`, `text-gray-700`, `bg-white`) that break
  theming — use semantic daisyUI colors.
- Flag untranslatable user-facing strings and missing German `msgstr` after catalog updates.

## Nachweis feature (Eigenbemühungen)

The **Nachweis von Eigenbemühungen** feature lives inside the `jobs` app
(`jobs/pdf.py`, `jobs/exports.py`, `jobs/tests_nachweis.py`, templates under
`jobs/templates/jobs/nachweis/`). Keep these constraints in kind when touching it:

- **Legal wording:** never claim BA/Jobcenter certification ("amtlich", "zertifiziert",
  logos, partnership). Allowed: "geeignet zur Dokumentation von Eigenbemühungen",
  "am amtlichen Formular orientiert", "kompatibel mit üblichen Nachweis-Anforderungen".
  No BA logo anywhere.
- **Official PDF labels are German literals** hardcoded in `jobs/pdf.py` — do NOT
  route them through gettext. UI strings follow the normal en→de catalog.
- **PDF generation** is WeasyPrint (system libs: `pango`, `cairo`, `gdk-pixbuf2`;
  on this host installed via dnf). `build_nachweis_pdf` /
  `build_nachweis_html` are pure functions — test them without request/DB.
- **Font:** `static/fonts/din1451alt.ttf` (Alte DIN 1451 Mittelschrift, Peter Wiegel,
  SIL OFL — license text kept next to it). Loaded server-side via `file://` URL by
  WeasyPrint; no collectstatic dependency for PDF rendering.
- **Invariants:** exports must never invent rows or fill in missing data (drafts are
  blockers); `applied_on` edits must append to `AuditLog` (see `Application.save`);
  empty exports are refused (`EmptyNachweisError` → redirect + message); PDF
  filenames follow `Nachweis_Eigenbemuehungen_YYYY-MM_Nachname.pdf`.
- **Quotas are user-configured** (ObligationPlan.required_count) — never hardcode
  "10 Bewerbungen/Monat"; there is no statutory nationwide number.
- **Compliance layer** (same app): `Vermittlungsvorschlag` (apply-by defaults to
  `received_on` + 3 *Werktage* via `add_workdays`; `has_rechtsfolgenbelehrung`;
  OPEN/APPLIED/DECLINED_WICHTIGER_GRUND/IGNORED), `Absence` (Ortsabwesenheit with
  `approval_status` — `PENDING` shows an unreported warning), `Obstacle` (wichtiger
  Grund). `ObligationPlan` carries the § 15a four-part tuple (`instrument`,
  `which_efforts`, `required_count`, `due_rule`, `proof_form`); `is_vague` /
  `missing_components` power the "plan not concrete" banner — a warning, never a
  block. Never treat "has a plan" as "will be sanctioned"; a Kooperationsplan alone
  is not enforceable (§ 15a Verpflichtungsbescheid / EGV + Rechtsfolgenbelehrung).
- `events.Event` gained `event_type='beratung'` (Meldetermin) and nullable `attended`.
- **Kostenbeleg:** `jobs/pdf.py` profile `KOSTENBELEG` prints costs + sum; the
  Nachweis PDFs (BA-Minimal / Jobcenter) must never show costs.
- Tests: `.venv/bin/python manage.py test jobs.tests_nachweis --noinput`.
- Evidence files use a dedicated local `FileSystemStorage`
  (`BASE_DIR/media/evidence`) on purpose — do not switch them to S3/object storage.

## Notes

- daisyUI skill is bundled at `.agents/skills/daisyui/SKILL.md` (managed via
  `npx skills add`, see `skills-lock.json`).
- If you change structure, commands, or conventions, update this file and `CLAUDE.md`.
- Keep changes minimal; prefer editing existing files over adding new ones.
