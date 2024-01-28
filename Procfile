release: python manage.py makemigrations gamestore && python manage.py migrate gamestore && python manage.py migrate
web: gunicorn gamestore.wsgi:application --log-file=-