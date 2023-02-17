# Contributing to Federated Model Aggregation (FMA) Service
First off, thanks for your input! We love to hear feedback from the community, and we want to make contributing to this
project as easy and transparent as possible, whether it is:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## We Develop with GitHub
We use GitHub to host code, track issues and feature requests, and accept improvements to the code through pull requests (PRs).

## Repository Components
This repo is created as a monolith of components pertaining to the FMA service.
The general workflow for development tips, tricks and testing for the components will be discussed here.
However, there are instructions on how to create virtual environments, run tests, and general helpful tips for
development in the components respective README.md files.

## Using Pipenv
All the repos components use a Pipfile to control dependencies and environment setup for their respective components.
As such, you will need to install Pipenv to be able to create an environment, run tests, as well as local test builds.
To install Pipenv run :
```
python -m pip install pipenv
```

## Dependencies
Each component has its own dependencies. This means that before installing dependencies you  must navigate to the required
component's directory with the following:
```
cd <./component_to_run_checks_on> #i.e aggregator
```
General and development dependencies are stored in the Pipfile within each component and will be installed to your virtual environment
via the following command:
```
pipenv install --dev
```

## Pre-Commit
To install `pre-commit` hooks in the top level, run the following commands:
```cli 
pipenv install pre-commit
pipenv run pre-commit install
```

To run hooks for all components:
```cli
pipenv run pre-commit run
```


To install and run the `pre-commit` hooks for a single component, `cd` into the component's directory 
and run the following commands:
```cli
pipenv run pre-commit install
pipenv run pre-commit run
```
Each component also has its own pre-commit checks that are specialized and differ slightly from one another,
to run precommit on a specific component, navigate to the top level of the component:
```
cd <./component_to_run_checks_on> #i.e aggregator
```
then simply run:
```
pipenv run pre-commit run --files ./
```

## Testing
Each component also comes with its own set of unit tests, to run these unit tests navigate to the component you wish to test:
```
cd <./component_to_run_tests_on> #i.e aggregator
```
and run the following to execute the tests: <br>
**Note**: Installation of pytest and its dependencies are handled by the [Dependencies](#Dependencies) section above
```
pipenv run pytest
```

## Creating [Pull Requests](https://github.com/capitalone/federated-model-aggregation/pulls)
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you have added code that should be tested, add tests.
3. If you have changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code passes `pre-commit` checks for the component(s) you have changed.
6. Issue that pull request!

## Any contributions you make will be under the Apache License 2.0
In short, when you submit code changes, your submissions are understood to be under the same [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) that covers the project. Feel free to contact the maintainers if that is a concern.

## Report bugs using Github's [Issues](https://github.com/capitalone/federated-model-aggregation/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/capitalone/federated-model-aggregation/issues/new); it is that easy!

## Write bug reports with detail, background, and sample code
Detailed bug reports will make fixing the bug significantly easier.

**Great Bug Reports** tend to have:
- General information of the working environment
- A quick summary of the bug
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- Screenshots of the bug
- Notes (possibly including why you think this might be happening, or stuff you tried that did not work)

People *love* thorough bug reports.

## Use a Consistent Coding Style
Please follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding conventions to maintain consistency in the repo. For
docstrings, please follow [reStructuredText](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) format as Sphinx is used to autogenerate
the documentation.
