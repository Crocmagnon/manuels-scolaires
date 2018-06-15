#!/bin/sh
yes yes | pipenv run python manage.py migrate && \
yes yes | pipenv run python manage.py createcachetable && \
pipenv run python manage.py collectstatic --noinput && \
pipenv run gunicorn manuels_collection.wsgi -b 0.0.0.0:8000 --log-file -
