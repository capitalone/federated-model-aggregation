HOME_DIR = $(shell pwd)

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
	PIPENV_VERBOSITY=-1                                \
	mkdir -p ./artifacts && 									 \
	cd ../../connectors/django/	&&  	 		        	   \
	pipenv run python setup.py sdist bdist_wheel &&    \
	cp -r dist/* ../../examples/django-deployment/artifacts/
	cd ../../fma-core	&&  	          							 \
	pipenv run python setup.py sdist bdist_wheel &&    \
	cp -r dist/* ../examples/django-deployment/artifacts/
