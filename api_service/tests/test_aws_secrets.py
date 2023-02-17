import os
from unittest import mock

import pytest
from botocore.exceptions import ClientError

from secrets_managers.aws_secrets import SecretException, get_secret

mock_environ = os.environ.copy()


@mock.patch("requests.get")
def test_get_secret_string_via_api(mock_get):
    mocked_secret = {"SecretString": "my-secret"}
    mock_get.return_value.json.return_value = mocked_secret

    secret_key = "my-secret"
    res = get_secret(secret_key)
    assert res == "my-secret"


@mock.patch("requests.get")
def test_get_secret_binary_via_api(mock_get):
    mocked_secret = {"SecretString": "my-secret"}
    mock_get.return_value.json.return_value = mocked_secret

    secret_key = "my-secret"
    res = get_secret(secret_key)
    assert res == "my-secret"


@mock.patch("os.environ", mock_environ)
def test_get_secret_via_env():

    mock_environ.update({"test": {"fake": "data"}})

    secret_key = "test"
    result = get_secret(secret_key)
    assert result == {"fake": "data"}


@mock.patch("requests.get")
def test_get_exception(mock_get):

    secret_key = "my-secret"

    error_messages = ["Failure: Cannot grab key from secret manager."]
    for error_message in error_messages:
        mock_get.return_value.json.side_effect = Exception("test")
        with pytest.raises(SecretException) as e_info:
            _ = get_secret(secret_key)
            assert e_info == error_message
