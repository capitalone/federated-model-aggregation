# FMA-Django

The FMA-Django component is a Django app that connects the FMA to django controlled databases or storage devices.
Detailed documentation is in the `./docs` directory.

Quick start
-----------
1. For installation, choose between just installing the db components or including the API as well.

```console
# install just the db / model connection component
pip install fma-django

# install the db / model / API connection component
pip install "fma-django[api]"
```

2. Add "fma-django" and "fma-django-api" to your INSTALLED_APPS setting like this:
```
    INSTALLED_APPS = [
        ...
        'fma_django',
        'fma_django_api',  # if the API is needed as well
    ]
```


3. Run ``python manage.py migrate`` to create the polls models (Django database tables).


Testing
-------

Inside a virtualenv:
```
make install
make test
```

For testing and coverage reports:
```
make test-and-coverage
```
