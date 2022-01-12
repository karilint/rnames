#!/bin/sh

# wait until connection to mariadb is successful
echo "CHECKING DATABASE CONNECTION"
python manage.py shell < ./scripts/check_db_connection.py || exit

echo
echo "RUNNING: MAKEMIGRATIONS & MIGRATE"
python manage.py makemigrations
python manage.py migrate

echo
echo "INITIALIZING DATABASE"
python manage.py shell < ./scripts/initialize.py

echo
echo "RUNNING TESTS"
python -u manage.py test -v2

echo
echo "STARTING DEVELOPMENT SERVER"
python manage.py livereload & disown
python manage.py runserver 0.0.0.0:8000
