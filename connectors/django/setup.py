"""Setup.py for fma-django."""
# To use a consistent encoding
import os
from codecs import open

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

# Load package version
from fma_django.version import __version__

project_path = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(project_path, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

# Get the install_requirements from requirements.txt
with open(os.path.join(project_path, "requirements.txt"), encoding="utf-8") as f:
    required_packages = f.read().splitlines()

# Get the api_install_requirements from requirements-api.txt
with open(os.path.join(project_path, "requirements-api.txt"), encoding="utf-8") as f:
    api_required_packages = f.read().splitlines()

DESCRIPTION = "Federated Model Aggregation Connectors"

packages = find_packages(exclude=["*.tests"])

setup(
    name="fma-django",
    author="Kenny Bean, Tyler Farnan, Taylor Turner, Michael Davis, Jeremy Goodsitt",
    version=__version__,
    python_requires=">=3.8",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
    ],
    # The project's main homepage.
    url="https://github.com/capitalone/federated-model-aggregation",
    # Choose your license
    license="Apache License, Version 2.0",
    keywords="Federated Learning",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['src/test', 'src/sample']),
    packages=packages,
    # List run-time dependencies here.  These will be installed by pip when
    # requirements files see:
    # your project is installed. For an analysis of "install_requires" vs pip's
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=required_packages,
    # List of run-time dependencies for the labeler. These will be installed
    # by pip when someone installs the project[<label>].
    extras_require={"api": api_required_packages},
    # # If there are data files included in your packages that need to be
    # # have to be included in MANIFEST.in as well.
    # # installed, specify them here.  If using Python 2.6 or less, then these
    include_package_data=True,
    data_files=None,
)

print("find_packages():", packages)
