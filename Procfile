web: python skill_share/manage.py collectstatic --noinput;
bin/gunicorn_django --workers=4 --bind=0.0.0.0:$PORT skill_share/settings.py 
