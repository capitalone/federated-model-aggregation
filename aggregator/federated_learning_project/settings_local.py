"""Django settings used for the local environment."""

import os
import sys

try:
    # TODO: abstract to file and remove only for testing locally
    import pysqlite3  # noqa: F401

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ModuleNotFoundError:
    pass

from .settings_base import *  # noqa: F403,F401

MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", "media_root")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
FIXTURE_DIRS = (os.path.join(PROJECT_ROOT, "tests/fixtures"),)

# local storage settings
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", "mediafiles")
MEDIA_URL = "/mediafiles/"

IS_LOCAL_DEPLOYMENT = True

try:
    IS_LAMBDA_DEPLOYMENT = bool(os.environ.get("IS_LAMBDA_DEPLOYMENT", False))
except Exception:
    IS_LAMBDA_DEPLOYMENT = False

if IS_LAMBDA_DEPLOYMENT:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/tmp/db.sqlite3",
        }
    }
    # TODO: fix workaround for lambda non-persistent memory to locally test
    import shutil

    shutil.copyfile("./db.sqlite3", "/tmp/db.sqlite3")
    shutil.copytree("./mediafiles/", "/tmp/mediafiles/")
    MEDIA_ROOT = "/tmp/mediafiles/"
