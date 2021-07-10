# manuels-scolaires
Help librarian manage textbooks requests from colleagues

## Local development

```bash
pipenv install
pipenv run python manage.py migrate
DJANGO_ENV=dev pipenv run python manage.py runserver
```

## Deploy on Heroku

```bash
heroku login
heroku git:remote --app manuels-scolaires
git push heroku master
```

You may need to upgrade Python since Heroku tends to deprecate old patch versions rather quickly.
In this case, edit `runtime.txt`.
