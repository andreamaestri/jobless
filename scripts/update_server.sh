#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-oci-django}"
REMOTE_REPO="${REMOTE_REPO:-/srv/django/jobless}"

if ! ssh -o BatchMode=yes "$REMOTE_HOST" 'sudo -n whoami >/dev/null'; then
  echo "Remote host requires passwordless sudo for $REMOTE_HOST" >&2
  exit 1
fi

printf '\n==> Copying dashboard application changes to remote server\n'
scp -o BatchMode=yes \
  jobs/views.py \
  jobs/urls.py \
  jobs/models.py \
  jobs/forms.py \
  jobs/tests.py \
  jobs/test_inline_endpoint.py \
  jobs/test_skills_taxonomy.py \
  "$REMOTE_HOST:$REMOTE_REPO/jobs/"
scp -o BatchMode=yes \
  jobs/templates/jobs/dashboard.html \
  "$REMOTE_HOST:$REMOTE_REPO/jobs/templates/jobs/dashboard.html"
scp -o BatchMode=yes \
  jobs/templates/jobs/widgets/skill_tree_widget.html \
  "$REMOTE_HOST:$REMOTE_REPO/jobs/templates/jobs/widgets/skill_tree_widget.html"
scp -o BatchMode=yes \
  jobs/fixtures/initial_skills.yaml \
  "$REMOTE_HOST:$REMOTE_REPO/jobs/fixtures/"
scp -o BatchMode=yes \
  jobs/management/commands/create_initial_skills.py \
  jobs/management/commands/create_initial_skills_enhanced.py \
  jobs/management/commands/populate_skills.py \
  jobs/management/commands/sync_skill_catalog.py \
  jobs/management/commands/validate_skills.py \
  "$REMOTE_HOST:$REMOTE_REPO/jobs/management/commands/"
scp -o BatchMode=yes \
  static/js/skill-tree-widget.js \
  "$REMOTE_HOST:$REMOTE_REPO/static/js/"
scp -o BatchMode=yes \
  jobs/templates/jobs/partials/plan_drawer.html \
  jobs/templates/jobs/partials/profile_drawer.html \
  jobs/templates/jobs/partials/application_drawer.html \
  "$REMOTE_HOST:$REMOTE_REPO/jobs/templates/jobs/partials/"
scp -o BatchMode=yes \
  home/context_processors.py \
  "$REMOTE_HOST:$REMOTE_REPO/home/context_processors.py"

printf '\n==> Building Tailwind assets on remote server\n'
ssh -o BatchMode=yes "$REMOTE_HOST" "bash -lc 'cd $REMOTE_REPO && export PYTHONPATH=\"$REMOTE_REPO/.venv/lib64/python3.12/site-packages\${PYTHONPATH:+:\$PYTHONPATH}\" && .venv/bin/python manage.py sync_skill_catalog'"
ssh -o BatchMode=yes "$REMOTE_HOST" "bash -lc 'cd $REMOTE_REPO && export PYTHONPATH=\"$REMOTE_REPO/.venv/lib64/python3.12/site-packages\${PYTHONPATH:+:\$PYTHONPATH}\" && .venv/bin/python manage.py tailwind build'"

printf '\n==> Collecting static files on remote server\n'
ssh -o BatchMode=yes "$REMOTE_HOST" "bash -lc 'cd $REMOTE_REPO && export PYTHONPATH=\"$REMOTE_REPO/.venv/lib64/python3.12/site-packages\${PYTHONPATH:+:\$PYTHONPATH}\" && .venv/bin/python manage.py collectstatic --noinput'"

printf '\n==> Restarting Jobless service\n'
ssh -o BatchMode=yes "$REMOTE_HOST" 'sudo systemctl restart jobless'

printf '\n==> Deploy finished\n'
