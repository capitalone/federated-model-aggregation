#!/usr/bin/python
"""Script which auto updates the github pages documentation."""
import imp
import os
import shutil
import subprocess
import sys
from pathlib import Path

branch_folder = "feature_branch"
branch_abs_path = os.path.abspath(f"../{branch_folder}")
sys.path.insert(0, os.path.abspath("."))

default_version = "0.0.1"
packages_to_build = [
    "aggregator",
    "api_service",  # order matters due to import of like folders w/ aggregator
    "clients/python_client",
    "connectors/django",
    "fma-core",
]

additional_paths_to_include = [
    "examples/client_examples/python_client",
]

all_env_paths = packages_to_build + additional_paths_to_include
# sets the env var to all paths in order to load in confs
os.environ["PACKAGE_PATHS"] = ";".join(
    map(
        lambda x: os.path.join(x[0], x[1]),
        zip([branch_abs_path] * len(all_env_paths), all_env_paths),
    )
)

versions_dict = {}
for pkg in packages_to_build:
    subprocess.run(
        [
            "sphinx-apidoc",
            "--templatedir=./source/_templates/",
            "-f",
            "-e",
            "-o",
            f"../docs/source/{pkg}/",
            f"../{branch_folder}/{pkg}/",
            "../*migrations*",
            "../*tests*",
            "../*setup*",
            "../*conftest*",
            "../*fma_settings*",
            "../*settings_*",
        ]
    )

    # Update version in rst files for building the html
    version = default_version
    version_path = sorted(Path(f"../{branch_folder}/{pkg}/").rglob("*version.py"))
    if version_path:
        pkg_version = imp.load_source("version", str(version_path[0]))
        version = pkg_version.__version__

        # Check if the source index file has already been updated
        update_index_rst = True
        source_index = open(f"source/{pkg}/index.rst", "r+")
        source_index_lines = source_index.readlines()
        source_index.close()
        for sentence in source_index_lines:
            if sentence.startswith("* `" + version):
                update_index_rst = False

        if update_index_rst:
            version_reference = ""
            buffer = 0
            source_index = open(f"source/{pkg}/index.rst", "w")
            for sentence in source_index_lines:
                if sentence.startswith("Documentation for"):
                    doc_version = "Documentation for " + version + "\n"
                    source_index.write(doc_version)
                elif sentence.startswith("Versions"):
                    source_index.write("Versions\n")
                    source_index.write("========\n")
                    version_tag = "* `" + version + "`_\n"
                    source_index.write(version_tag)
                    version_reference = (
                        ".. _" + version + ": ../../" + version + "/html/index.html\n\n"
                    )
                    buffer = 1
                else:
                    if buffer == 0:
                        source_index.write(sentence)
                    else:
                        buffer = buffer - 1
            source_index.write(version_reference)
            source_index.close()

    versions_dict[pkg] = version

    # Make the html files
    build_directory = f"BUILDDIR=build/{pkg}/{version}"
    source_directory = f"SOURCEDIR=source/{pkg}"
    subprocess.run(["make", "html", source_directory, build_directory])

# convert django-deployment example README to RST
subprocess.run(
    [
        "pandoc",
        "../feature_branch/examples/django-deployment/README.md",
        "--from markdown",
        "--to rst",
        "-s",
        "-o",
        "../docs/source/examples/django_example.rst",
    ]
)

# now run in the root of `/docs` to generate the index and top level
# HTML files
subprocess.run(
    [
        "make",
        "html",
        "SOURCEDIR=source",
        "BUILDDIR=build",
    ]
)


# now copy over the needed folder(s)
# and files to the root of /build
shutil.move("build/html/index.html", "build/index.html")
shutil.move("build/html/api_endpoints.html", "build/api_endpoints.html")
shutil.move("build/html/setup.html", "build/setup.html")
shutil.move("build/html/examples.html", "build/examples.html")
shutil.move("build/html/django_example.html", "build/django_example.html")
shutil.move("build/html/client_example.html", "build/client_example.html")
shutil.move("build/html/genindex.html", "build/genindex.html")
shutil.move("build/html/searchindex.js", "build/searchindex.js")
shutil.move("build/html/objects.inv", "build/objects.inv")
shutil.move("build/html/search.html", "build/search.html")
shutil.move("build/html/roadmap.html", "build/roadmap.html")

try:
    shutil.move("build/html/_images/", "build/")
except shutil.Error:
    pass

try:
    shutil.move("build/html/_static/", "build/")
except shutil.Error:
    pass

try:
    os.mkdir("build/_sources/")
except FileExistsError:
    pass

shutil.move("build/html/_sources/index.rst.txt", "build/_sources/index.rst.txt")
shutil.move("build/html/_sources/setup.rst.txt", "build/_sources/setup.rst.txt")
shutil.move("build/html/_sources/examples.rst.txt", "build/_sources/examples.rst.txt")
shutil.move("build/html/_sources/roadmap.rst.txt", "build/_sources/roadmap.rst.txt")
shutil.move(
    "build/html/_sources/django_example.rst.txt",
    "build/_sources/django_example.rst.txt",
)
shutil.move(
    "build/html/_sources/client_example.rst.txt",
    "build/_sources/client_example.rst.txt",
)
# ORDER MATTERS TO THIS! THIS MUST BE LAST!
shutil.rmtree("build/html/")

# update lines 117 - 123 in `build/index.html
# to go to the most up to date version of the sub module documentation
no_link_html = (
    '<li class="toctree-l1"><a class="reference external" '
    'href="http://localhost/replaceme">Aggregator</a></li>\n'
    '<li class="toctree-l1"><a class="reference external" '
    'href="http://localhost/replaceme">API Service</a></li>\n'
    '<li class="toctree-l1"><a class="reference external" '
    'href="http://localhost/replaceme">FMA Django</a></li>\n'
    '<li class="toctree-l1"><a class="reference external" '
    'href="http://localhost/replaceme">FMA Connect</a></li>\n'
    '<li class="toctree-l1"><a class="reference external" '
    'href="http://localhost/replaceme">FMA Core</a></li>\n'
)

link_html_string = (
    f'<li class="toctree-l1"><a class="reference internal" '
    f'href="aggregator/{versions_dict["aggregator"]}'
    f'/html/index.html">Aggregator</a></li>\n'
    f'<li class="toctree-l1"><a class="reference internal" '
    f'href="api_service/{versions_dict["api_service"]}'
    f'/html/index.html">API Service</a></li>\n'
    f'<li class="toctree-l1"><a class="reference internal" '
    f'href="connectors/django/{versions_dict["connectors/django"]}'
    f'/html/index.html">FMA Django</a></li>\n'
    f'<li class="toctree-l1"><a class="reference internal" '
    f'href="clients/python_client/{versions_dict["clients/python_client"]}'
    f'/html/index.html">FMA Connect</a></li>\n'
    f'<li class="toctree-l1"><a class="reference internal" '
    f'href="fma-core/{versions_dict["fma-core"]}'
    f'/html/index.html">FMA Core</a></li>\n'
)

top_level_html = [
    "build/index.html",
    "build/api_endpoints.html",
    "build/setup.html",
    "build/examples.html",
    "build/django_example.html",
    "build/client_example.html",
    "build/roadmap.html",
]
for doc in top_level_html:
    with open(doc, "r") as f:
        # pull current data
        data_read_string = f.read()
        new_content = data_read_string.replace(no_link_html, link_html_string)
        f.close()

        # now open in overwrite mode and write new content
        f = open(doc, "w")
        f.write(new_content)
        f.close()
