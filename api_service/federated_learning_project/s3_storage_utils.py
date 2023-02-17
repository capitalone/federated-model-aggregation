"""Module created for s3 linkage in settings files."""

from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Class used for linkage to s3 bucket for settings file."""

    bucket_name = "fma-serverless-storage"
    location = "static"
