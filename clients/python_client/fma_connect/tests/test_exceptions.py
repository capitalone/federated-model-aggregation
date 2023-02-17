import os
import sys
import unittest

TEST_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_ROOT_DIR = os.path.dirname(TEST_ROOT_DIR)
sys.path.append(CLIENT_ROOT_DIR)
from fma_connect import exceptions  # noqa: E402


class TestApiException(unittest.TestCase):
    def test_init(self):

        exception = exceptions.APIException()
        self.assertEqual(
            "An API error occurred (status_code=NULL): Could not connect to "
            "the server.",
            str(exception),
        )

        exception = exceptions.APIException(403, {"detail": "unauthorized"})
        self.assertEqual(
            "An API error occurred (status_code=403): " "{'detail': 'unauthorized'}",
            str(exception),
        )
