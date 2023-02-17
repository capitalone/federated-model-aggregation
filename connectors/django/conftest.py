"""Sets root directory for repo."""
import logging
import os
import sys
from os.path import abspath, dirname, join

from django.conf import settings

log = logging.Logger(name=__file__)
root_dir = dirname(abspath(__file__))
sys.path.append(root_dir)
os.environ["FMA_SETTINGS_MODULE"] = "fma_django_connectors.tests.fma_settings"
os.environ["FMA_DB_SECRET_PATH"] = "fake/path"

settings.configure(
    DEBUG=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
        }
    },
    ALLOWED_HOSTS=["127.0.0.1", "localhost"],
    FIXTURE_DIRS=(join(root_dir, "tests/fixtures"),),
    INSTALLED_APPS=(
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # MPTT install
        "mptt",
        # REST API
        "rest_framework",
        "rest_framework.authtoken",
        "django_filters",
        # task management
        "django_q",
        # app
        "fma_django",
    ),
    SECRET_KEY="TESTING",
    USE_TZ=True,
    LANGUAGE_CODE="en-us",
    TIME_ZONE="UTC",
    USE_I18N=True,
    IS_LOCAL_DEPLOYMENT=True,
    # API reqs
    ROOT_URLCONF="fma_django_api.urls",
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.BasicAuthentication",
            "rest_framework.authentication.SessionAuthentication",
            "fma_django.authenticators.ClientAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ),
        "DEFAULT_FILTER_BACKENDS": (
            "django_filters.rest_framework.DjangoFilterBackend",
            "rest_framework.filters.OrderingFilter",
        ),
    },
    MEDIA_URL="/mediafiles/",
)
