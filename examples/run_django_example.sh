cd django-deployment
make compile-packages
make install
brew install redis
pipenv run python3 manage.py migrate
pipenv run python manage.py createsuperuser
FMA_SETTINGS_MODULE=federated_learning_project.fma_settings pipenv run python manage.py runserver &
redis-server &
FMA_SETTINGS_MODULE=federated_learning_project.fma_settings pipenv run python manage.py qcluster & fg


