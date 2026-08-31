# AGENTS.md

Project-specific instructions for coding agents working on **Jobless** — a Django 5.1
job-search tracker. Complements the human-facing `README.md` and the more detailed
`CLAUDE.md`.

## Setup

- Python venv lives at `.venv/`; all Django commands run through it, e.g.
  `.venv/bin/python manage.py ...` with `DJANGO_SETTINGS_MODULE=config.settings.production`
  (or source the bundled `.env`).
- JS dependencies: `npm install` at repo root (Vite) and `python manage.py tailwind install`
  for the `theme/` app.
- Run the dev server with `python manage.py runserver` and `npm run dev` for Vite HMR.

## Commands

- System check: `.venv/bin/python manage.py check`
- Tests: `python manage.py test` (per-app: `test jobs|contacts|events`)
- Frontend assets: Vite build `npm run build`; Tailwind build `python manage.py tailwind build`;
  collect with `python manage.py collectstatic --noinput`
- i18n: `makemessages -l de`, `compilemessages`; validate catalogs with
  `msgfmt --check-format locale/de/LC_MESSAGES/django.po`
- Production (systemd `jobless.service`, Gunicorn on `127.0.0.1:8001`):
  `source /etc/jobless.env` then migrate/collect/restart; live page checks use a Django test
  client with `Client(SERVER_NAME="localhost")` and `secure=True`

## Conventions

- UI: daisyUI 5 + Tailwind CSS 4 (CSS-first in `theme/static_src/src/styles.css`).
  Custom themes (Jobless/Dark) are registered there — `tailwind.config.js` files are
  intentionally ignored. Use daisyUI semantic colors (`bg-base-100`, `text-base-content`,
  etc.) and current v5 classes (`fieldset`, `join`, `tabs-box`). The work tree contains a
  bundled skill: `.agents/skills/daisyui/SKILL.md`.
- Never put `@apply` inside template `<style>` blocks; put the styles in `styles.css` instead.
- i18n: English is the source language; keep templates translatable with
  `{% translate %}` / `gettext_lazy`, and add German `msgstr` entries to
  `locale/de/LC_MESSAGES/django.po` (compile `.mo` afterwards). Model choices are
  wrapped in `gettext_lazy`.
- URLs are namespaced (`jobs:list`, `contacts:detail`, ...); templates reference them by name.
- Models reference users via `settings.AUTH_USER_MODEL`; candidate JS labels for
  JavaScript catalogs live in `locale/de/LC_MESSAGES/djangojs.po`.

## Code Review Rules

- Flag daisyUI 4-era classes (`form-control`, `input-bordered`, `select-bordered`,
  `btn-primary-focus`, `tabs-boxed`, `input-group`) — replace with v5 equivalents.
- Flag hardcoded palette classes (`bg-green-100`, `text-gray-700`, `bg-white`) that break
  theming — use semantic daisyUI colors.
- Flag untranslatable user-facing strings and missing German `msgstr` after catalog updates.
- Avoid committing `staticfiles/` artifacts; compiled theme CSS at
  `theme/static/css/dist/` is tracked deliberately (build locally, deploy with collectstatic).

## Notes

- If you change structure, commands, or conventions, update this file and `CLAUDE.md`.
- Keep changes minimal; prefer editing existing files over adding new ones.
