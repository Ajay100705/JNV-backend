#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py migrate
python manage.py create_initial_admin
python manage.py collectstatic --noinput