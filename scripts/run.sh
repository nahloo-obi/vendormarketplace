#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate
echo "Migrations has been done"
uwsgi --socket :9000 --workers 4 --master --enable-threads --module vendor_marketplace.wsgi
