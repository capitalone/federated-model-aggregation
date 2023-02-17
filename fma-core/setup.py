"""Setup.py for fma algorithms."""
import os

from setuptools import find_packages, setup

from fma_core.version import __version__

project_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(project_path, "requirements.txt"), encoding="utf-8") as f:
    required_packages = f.read().splitlines()

with open(os.path.join(project_path, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

DESCRIPTION = "Federated Model Aggregation Algoithms"

packages = find_packages(exclude=["*.tests"])

setup(
    author="Kenny Bean, Tyler Farnan, Taylor Turner, Michael Davis, Jeremy Goodsitt ",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    data_files=None,
    description=DESCRIPTION,
    include_package_data=True,
    install_requires=required_packages,
    keywords="Federated Learning",
    license="Apache License, Version 2.0",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    name="fma-core",
    packages=packages,
    python_requires=">=3.8",
    url="https://github.com/capitalone/federated-model-aggregation",
    version=__version__,
)

print("find_packages():", packages)
