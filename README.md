Local deployment
REQUIRED PYTHON - 3.6.1
================================

### Install project requirements
    $ pip install -r requirements.txt

### Create local settings file
    $ cp archer/local_settings archer/local_settings.py

### Run migrations
    $ python manage.py migrate

### Run tests
    $ python manage.py test

### Run server
    $ python manage.py runserver 127.0.0.1:8000
    
### Creare superuser
    $ python manage.py createsuperuser

### All API endpoints in swagger page at runserver 127.0.0.1:8000/docs/ (authorize as with superuser creds)
