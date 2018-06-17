#!/bin/sh
set -x -e
# Wait until DB is up
# TODO: Is there a better way to check this?
until python -c "import psycopg2; \
                 psycopg2.connect( \
                      dbname='dmarc_viewer_db', \
                      user='dmarc_viewer_db', \
                      host='${DMARC_VIEWER_DB_HOST}', \
                      password='${DMARC_VIEWER_DB_KEY}')"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# NOTE: Below management commands are no-ops if they ran before
# Populate initial DMARC viewer db model
>&2 echo "Setup DB"
python manage.py makemigrations website --noinput
python manage.py migrate --noinput

# Collect and copy required static web assets
# (see sdmarc_viewer.ettings.STATIC_ROOT)
>&2 echo "Collect and move static files"
python manage.py collectstatic --noinput

# Change cache dir ownership (see dmarc-viewer/dmarc-viewer#10)
# The cache dir is created when running `makemigrations` above (as root), but
# the uwsgi daemon is running with `UWSGI_UID` (see Dockerfile)
chown ${UWSGI_UID} /var/tmp/django_cache

exec "$@"
