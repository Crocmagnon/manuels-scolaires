release: python manage.py migrate && python manage.py createcachetable && python manage.py clearcache
web: gunicorn manuels_collection.wsgi --log-file -
