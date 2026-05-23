#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements/production.txt

# Collect static files (clear old files first)
python manage.py collectstatic --no-input --clear

# Run migrations
python manage.py migrate
