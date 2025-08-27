#!/bin/bash

poetry install
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
gunicorn stashcontrol.wsgi