HOME_DIR = $(shell pwd)
USER_BIN_PATH = $(shell python3 -m site --user-base)/bin
PG_CONFIG_PATH = $(shell which pg_config)
PIP_PATH = $(shell which pip)

.PHONY: install
install:
	pipenv --rm || true
	pipenv --clear
	rm -f Pipfile.lock
	pipenv install --dev
	pipenv run pre-commit install

.PHONY: test
test:
	pipenv run pytest

.PHONY: test-and-coverage
test-and-coverage:
	pipenv run pytest --junit-xml=junit_xml_test_report.xml --cov-branch --cov=fma_algorithms .
	pipenv run coverage xml -i
	pipenv run coverage report --fail-under 80


.PHONY: compile-packages
compile-packages:
	PIPENV_VERBOSITY=-1 \
	mkdir -p ./artifacts && \
	cd ../../connectors/django && \
	pipenv run python setup.py sdist bdist_wheel && \
	cp -r dist/* ../../examples/django-deployment/artifacts/
	cd ../../fma-core	&& \
	pipenv run python setup.py sdist bdist_wheel && \
	cp -r dist/* ../examples/django-deployment/artifacts/


.PHONY: complete-install
complete-install:

ifeq (${PIP_PATH},)
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	python ./get-pip.py
endif

ifeq (${PG_CONFIG_PATH},)
ifeq ($(shell uname -s), Linux)
	apt-get -y install postgresql
else ifeq ($(shell uname -s), Darwin)
	brew install postgresql
else
	echo "Error! postgresql not supported by $(shell uname -s)"
	exit 125
endif
endif

ifneq ($(shell pip list | grep pipenv | cut -d ' ' -f1),pipenv)
	pip install --user pipenv
endif

	export PATH=${PATH}:${USER_BIN_PATH} && \
	make compile-packages && make install

ifeq ($(shell uname -s), Linux)
	apt-get install redis
else ifeq ($(shell uname -s),Darwin)
	brew install redis
else
	echo "Error! redis not supported by $(shell uname -s)"
	exit 125
endif
	export FMA_SETTINGS_MODULE=federated_learning_project.fma_settings
	pipenv run python manage.py migrate
	pipenv run python manage.py createsuperuser


.PHONY: start-service-local
start-service-local:
	export FMA_SETTINGS_MODULE=federated_learning_project.fma_settings
	pipenv run python manage.py runserver & redis-server & pipenv run python manage.py qcluster &


.PHONY: kill-service-local
kill-service-local:
	pkill -f manage.py || true
	pkill -f redis || true
	pkill -f qcluster || true
