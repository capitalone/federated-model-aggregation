cd django-deployment
export FMA_SETTINGS_MODULE=federated_learning_project.fma_settings
pipenv run python3 manage.py migrate
pipenv run python manage.py createsuperuser
pipenv run python manage.py runserver & redis-server & pipenv run python manage.py qcluster