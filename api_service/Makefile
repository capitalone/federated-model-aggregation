.PHONY: install
install:
	pipenv --rm || true
	pipenv --clear
	rm -rf Pipfile.lock
	pipenv install --dev
	pipenv run pre-commit install

.PHONY: test
test:
	pipenv run pytest

.PHONY: test-and-coverage
test-and-coverage:
	pipenv run pytest --junit-xml=junit_xml_test_report.xml --cov-branch --cov=. .
	pipenv run coverage xml -i
	pipenv run coverage report --fail-under 80

.PHONY: sam-build-local
sam-build-local:
	PIPENV_VERBOSITY=-1                                                      \
	pipenv requirements --dev > requirements.txt &&                              \
	pipenv run echo "pysqlite3-binary" >> requirements.txt &&                \
	pipenv run sam build --skip-pull-image --use-container --debug

.PHONY: sam-build-remote
sam-build-remote:
	PIPENV_VERBOSITY=-1                                                               \
	pipenv requirements > requirements.txt &&                                         \
	pipenv run sam build --debug --use-container --template=./template-remote.yaml

.PHONY: build-FmaServerless
build-FmaServerless:
	mkdir -p "$(ARTIFACTS_DIR)"
	cp -r ./* "$(ARTIFACTS_DIR)"
	python -m pip install -r requirements.txt -t "$(ARTIFACTS_DIR)" --find-links ./artifacts
	python "$(ARTIFACTS_DIR)"/manage.py migrate
	python "$(ARTIFACTS_DIR)"/manage.py loaddata tests/fixtures/TaskQueue_User.json
	python "$(ARTIFACTS_DIR)"/manage.py loaddata tests/fixtures/TaskQueue_client.json
	python "$(ARTIFACTS_DIR)"/manage.py loaddata tests/fixtures/DjangoQ_Schedule.json
	python "$(ARTIFACTS_DIR)"/manage.py loaddata tests/fixtures/DjangoQ_Task.json
	python "$(ARTIFACTS_DIR)"/manage.py loaddata tests/fixtures/TaskQueue_FederatedModel.json
	python "$(ARTIFACTS_DIR)"/manage.py loaddata tests/fixtures/TaskQueue_ModelAggregate.json
	python "$(ARTIFACTS_DIR)"/manage.py loaddata tests/fixtures/TaskQueue_ModelArtifact.json
	python "$(ARTIFACTS_DIR)"/manage.py loaddata tests/fixtures/TaskQueue_ModelUpdate.json
	python "$(ARTIFACTS_DIR)"/manage.py collectstatic --no-input
	cp -a tests/fixtures/mediafiles/. "$(ARTIFACTS_DIR)"/mediafiles/

.PHONY: sam-local
sam-local:
	PIPENV_VERBOSITY=-1 pipenv run sam local start-api --skip-pull-image --log-file ./out.log --warm-containers LAZY

.PHONY: fma-django-compile
fma-django-compile:
	PIPENV_VERBOSITY=-1
	rm -rf artifacts	&&																										 \
	cd ../connectors/django &&																							 \
	pipenv run python setup.py sdist bdist_wheel &&                          \
	mkdir -p ../../api_service/artifacts && 																 \
	cp -r dist/* ../../api_service/artifacts/   &&                           \
	cd ../../fma-core	&&  	          							                         \
	pipenv run python setup.py sdist bdist_wheel &&   											 \
	cp -r dist/* ../api_service/artifacts/
