source ../venv/bin/activate

python manage.py makemigrations
python manage.py migrate
python manage.py shell < utils/createsuperuser.py
python manage.py runserver 