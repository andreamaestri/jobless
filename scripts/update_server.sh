#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-oci-django}"
REMOTE_REPO="${REMOTE_REPO:-/srv/django/jobless}"

if ! ssh -o BatchMode=yes "$REMOTE_HOST" 'sudo -n whoami >/dev/null'; then
  echo "Remote host requires passwordless sudo for $REMOTE_HOST" >&2
  exit 1
fi

printf '\n==> Copying local template changes to remote server\n'
scp -o BatchMode=yes templates/base.html "$REMOTE_HOST:$REMOTE_REPO/templates/base.html"

printf '\n==> Building Tailwind assets on remote server\n'
ssh -o BatchMode=yes "$REMOTE_HOST" "bash -lc 'cd $REMOTE_REPO && export PYTHONPATH=\"$REMOTE_REPO/.venv/lib64/python3.12/site-packages\${PYTHONPATH:+:\$PYTHONPATH}\" && .venv/bin/python manage.py tailwind build'"

printf '\n==> Collecting static files on remote server\n'
ssh -o BatchMode=yes "$REMOTE_HOST" "bash -lc 'cd $REMOTE_REPO && export PYTHONPATH=\"$REMOTE_REPO/.venv/lib64/python3.12/site-packages\${PYTHONPATH:+:\$PYTHONPATH}\" && .venv/bin/python manage.py collectstatic --noinput'"

printf '\n==> Restarting Jobless service\n'
ssh -o BatchMode=yes "$REMOTE_HOST" 'sudo systemctl restart jobless'

printf '\n==> Deploy finished\n'
