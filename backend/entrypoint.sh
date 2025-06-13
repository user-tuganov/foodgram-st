#!/bin/sh

set -e

python manage.py makemigrations --noinput
python manage.py migrate --noinput

python manage.py add_ingredients

python manage.py create_super_user

mkdir -p /app/static /app/media
python manage.py collectstatic --noinput

chmod -R 755 /app/static /app/media

exec "$@"
