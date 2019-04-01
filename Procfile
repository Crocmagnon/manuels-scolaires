release: python manage.py migrate && python manage.py createcachetable
web: gunicorn manuels_collection.wsgi --log-file -
