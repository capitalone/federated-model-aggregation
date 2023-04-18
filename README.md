# federated-model-aggregation
## Description
This repo is dedicated to the installation/distribution of components of the Federated Model Aggregation service.

Visit our [documentation page.](https://capitalone.github.io/federated-model-aggregation/)

### How to properly write documentation:

#### Packages
In any package directory, overall package comments can be made in the
\_\_init\_\_.py of the directory. At the top of the \_\_init\_\_.py,
include your comments in between triple quotations.

#### Classes
In any class file, include overall class comments at the top of the file
in between triple quotes and/or in the init function.

#### Functions
reStructuredText Docstring Format is the standard. Here is an example:

    def format_data(self, predictions, verbose=False):
        """
        Formats word level labeling of the Unstructured Data Labeler as you want

        :param predictions: A 2D list of word level predictions/labeling
        :type predictions: Dict
        :param verbose: A flag to determine verbosity
        :type verbose: Bool
        :raises: Exception
        :return: JSON structure containing specified formatted output
        :rtype: JSON

        :Example:
            Look at this test. Don't forget the double colons to make a code block::
                This is a codeblock
                Type example code here
        """

### How to update the documentation:

1. Either with an existing clone of `capitalone/federated-model-aggregation` or clone the `capitalone/federated-model-aggregation` reposotory to your local computer with the following command:
```bash
git clone https://github.com/capitalone/federated-model-aggregation.git
```

2. Next ensure that `gh-pages` branch is checked out in `federated-model-aggregation` repository folder:
```bash
cd federated-model-aggregation
git checkout gh-pages
```

3. Next inside `federated-model-aggregation` repo that we just cloned down to your local machine, clone the repository under the alias `feature_branch` inside the root of `federated-model-aggregation` from step one:
```bash
git clone https://github.com/capitalone/federated-model-aggregation.git feature_branch
```

4. Still in the root of `federated-model-aggregation`, install the requirements needed for generating the documentation:
```bash
# install sphinx requirements
brew install pandoc

# setup virtualenv
python3 -m venv venv-ghpages

# activate virtulaenv
. venv-ghpages/bin/activate

# install python reqs for gh-pages
pip install -r requirements.txt

# install django project requirements from feature branch
pip install -r feature_branch/connectors/django/requirements.txt
pip install -r feature_branch/connectors/django/requirements-api.txt
```

5. And finally, from the root of `federated-model-aggregation`, run the following commands to generate the sphinx documentation:
```bash
cd docs/
make all-docs

# One can manually clean and update docs once within the `docs` folder
make clean
python update_documentation.py
```

If you make adjustments to the code comments, you may rerun the command again to overwrite the specified version.

Once the documentation is updated, commit and push the whole
`/docs` folder as well as the `index.html` file. API documentation
will only update when merged to the `capitalone/federated-model-aggregation` `gh-pages` branch.

If you make a mistake naming the version, you will have to delete it from
the /docs/source/index.rst file.

To update the documentation of a feature branch, go to the /docs folder
and run:
```bash
cd docs
python update_documentation.py
```
