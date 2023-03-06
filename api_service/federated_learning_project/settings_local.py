"""Django settings used for the local environment."""

import os
import sys

# added for testing circular imports
from fma_core.conf import settings as fma_settings  # noqa: F401

try:
    # TODO: abstract to file and remove only for testing locally
    import pysqlite3  # noqa: F401

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ModuleNotFoundError:
    pass

from .settings_base import *  # noqa: F403,F401

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# local storage settings
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
FIXTURE_DIRS = (os.path.join(PROJECT_ROOT, "tests/fixtures"),)

STATIC_URL = "/static/"
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", "mediafiles")
MEDIA_URL = "/mediafiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405

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
    shutil.copytree("./mediafiles/", "/tmp/mediafiles/", dirs_exist_ok=True)
    MEDIA_ROOT = "/tmp/mediafiles/"
