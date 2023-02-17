# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import furo
import os
import sys
import re


for path in os.environ.get("PACKAGE_PATHS", "").split(';'):
    sys.path.insert(0, path)

# -- Project information -----------------------------------------------------

project = "FMA Severless"
copyright = "2023, Kenny Bean, Tyler Farnan, Taylor Turner, Michael Davis,  Jeremy Goodsitt",
author = "Taylor Turner"

# # The full version, including alpha/beta/rc tags
# version = "0.0.1"


# version_clip = re.search(r'\s*([\d.]+)', version).group(1)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'furo',
    'sphinx.ext.intersphinx',
    "myst_parser",
]

autoclass_content = 'both'
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'inherited-members': True,
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# TODO -- add images for docs below
html_theme = "furo"
html_title = f"<div class='title'>Federated Model Aggregation</div>"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
# html_favicon = "no_pic"
# html_theme_options = {
#     "light_logo": "no_pic",
#     "dark_logo": "no_pic",
# }
