#!/bin/bash

export DJANGO_SECRET_KEY='lmaoooo'
export DB_ENGINE=django.db.backends.postgresql_psycopg2
export POSTGRES_DB=quizzle
export POSTGRES_USER=user
export POSTGRES_PASSWORD=password
export POSTGRES_HOST=db
export POSTGRES_PORT=5432

python manage.py makemigrations 
python manage.py migrate
python manage.py shell < utils/createsuperuser.py
python manage.py runserver 0.0.0.0:8000