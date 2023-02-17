"""Utility functionality used to grab secrets from AWS Secrets Manager."""
import json
import os

import requests

_secret_cache = {}


class SecretException(Exception):
    """Overarching secret handler class."""

    pass


def get_secret(secret_name):
    """
    Gets secret info from a folder path.

    :param secret_name: name of secret
    :type secret_name: str
    :return: Secret Token
    :rtype: Union[str, int, float, bool, None, List, Dict]
    """
    secret_extension_port = os.environ.get(
        "PARAMETERS_SECRETS_EXTENSION_HTTP_PORT", "2773"
    )
    endpoint = f"http://localhost:{secret_extension_port}"
    secret_path = os.environ["FMA_DB_SECRET_PATH"]

    value = os.getenv(secret_name, None)
    try:
        value = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        pass

    if value is None:
        try:
            # Secrets rotation will require more attributes of this request
            secrets_extension_endpoint = (
                f"{endpoint}/secretsmanager/get?secretId={secret_name}"
            )
            response = requests.get(secrets_extension_endpoint)
            secret_data = response.json().get("SecretString")
            if secret_data is not None:
                value = secret_data
                _secret_cache[secret_path] = value
        except Exception as e:
            raise SecretException(
                "Failure: Cannot grab key from AWS secrets manager."
            ) from e
    return value or ""
