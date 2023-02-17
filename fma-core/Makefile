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
	pipenv run pytest --junit-xml=junit_xml_test_report.xml --cov-branch --cov=fma_core .
	pipenv run coverage xml -i
	pipenv run coverage report --fail-under 80
