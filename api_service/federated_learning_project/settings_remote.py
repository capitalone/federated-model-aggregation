"""Django settings used for the remote environment."""
import importlib
import os

from fma_core.conf import settings as fma_settings

from .settings_base import *  # noqa: F401,F403


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ENVIRONMENT VARS
fma_database_name = os.environ["FMA_DATABASE_NAME"]
fma_database_host = os.environ["FMA_DATABASE_HOST"]
fma_database_port = os.environ["FMA_DATABASE_PORT"]
SECRETS_PATH = os.environ["FMA_DB_SECRET_PATH"]

# PLACEHOLDER VARS NEEDED TO BE SET HERE
TRUSTED_ORIGIN = "<TMP_TRUSTED_ORIGIN>"
AGGREGATOR_LAMBDA_ARN = os.environ.get("LAMBDA_INVOKED_FUNCTION_ARN", "")


secrets_manager = importlib.import_module(
    "secrets_managers." + fma_settings.AGGREGATOR_SETTINGS["secrets_manager"]
)

ALLOWED_HOSTS = [
    "loadbalancer",
    "localhost",
    "127.0.0.1",
    TRUSTED_ORIGIN,
]
CSRF_TRUSTED_ORIGINS = ["https://" + TRUSTED_ORIGIN]

# TODO: Change to ENV var
db_secret = secrets_manager.get_secret(SECRETS_PATH)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": fma_database_name,
        "USER": list(db_secret.keys())[0],
        "PASSWORD": list(db_secret.values())[0],
        "HOST": fma_database_host,
        "PORT": fma_database_port,
    }
}

# aws settings
AWS_STORAGE_BUCKET_NAME = "fma-serverless-storage"
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

# s3 static settings
STATIC_URL = "/static/"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "federated_learning_project.s3_storage_utils.StaticStorage"

MEDIA_URL = "/mediafiles/"

IS_LOCAL_DEPLOYMENT = False

TAGS = {
    # """<TMP_TAGKEY>""": """<TMP_TAGVALUE>""",
}
