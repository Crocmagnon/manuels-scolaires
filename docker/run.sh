#!/bin/bash
set -eux
python manage.py migrate --noinput
python manage.py createcachetable
python manage.py clearcache
gunicorn manuels_collection.wsgi -b 0.0.0.0:8000 --log-file -
