import os
import sys
import unittest
import urllib.parse
from unittest import mock

TEST_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_ROOT_DIR = os.path.dirname(TEST_ROOT_DIR)
sys.path.append(CLIENT_ROOT_DIR)
import fma_connect  # noqa: E402
import fma_connect.settings  # noqa: E402
from fma_connect import exceptions  # noqa: E402


class TestWebClient(unittest.TestCase):
    def test_init(self):

        # only setting federated_model_id
        client = fma_connect.WebClient(federated_model_id=1)
        self.assertEqual(1, client.federated_model_id)
        self.assertEqual(None, client._uuid)
        self.assertEqual(fma_connect.settings.default_url, client.url)
        self.assertFalse(client._is_registered)
        self.assertIsNone(client._last_model_aggregate)

        #  setting url
        client = fma_connect.WebClient(federated_model_id=1, url="http://test.com")
        self.assertEqual(1, client.federated_model_id)
        self.assertEqual(None, client._uuid)
        self.assertEqual("http://test.com", client.url)
        self.assertFalse(client._is_registered)
        self.assertIsNone(client._last_model_aggregate)

        #  setting url and uuid
        client = fma_connect.WebClient(
            federated_model_id=1,
            url="http://test.com",
            uuid="ab359e5d-6991-4088-8815-a85d3e413c02",
        )
        self.assertEqual(1, client.federated_model_id)
        self.assertEqual("ab359e5d-6991-4088-8815-a85d3e413c02", client.uuid)
        self.assertEqual("http://test.com", client.url)
        self.assertFalse(client._is_registered)
        self.assertIsNone(client._last_model_aggregate)

    @mock.patch("requests.post")
    def test_register(self, mock_post):

        # validate server error
        client = fma_connect.WebClient(federated_model_id=1)
        mock_post.return_value.status_code = 403
        mock_post.return_value.json.return_value = {"detail": "unauthorized"}
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.register()
        self.assertFalse(client._is_registered)
        self.assertIsNone(client._last_model_aggregate)

        # validate success, no uuid
        client = fma_connect.WebClient(federated_model_id=1)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"uuid": "fake-uuid"}
        uuid = client.register()
        self.assertEqual("fake-uuid", uuid)
        self.assertEqual("fake-uuid", client.uuid)
        url = urllib.parse.urljoin(
            fma_connect.settings.default_url, "/api/v1/models/1/register_client/"
        )
        mock_post.assert_called_with(url, headers=None, timeout=10)
        self.assertTrue(client._is_registered)
        self.assertIsNone(client._last_model_aggregate)

        # validate success, no uuid
        client = fma_connect.WebClient(federated_model_id=1, uuid="fake-uuid")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"uuid": "fake-uuid"}
        uuid = client.register()
        self.assertEqual("fake-uuid", uuid)
        self.assertEqual("fake-uuid", client.uuid)
        url = urllib.parse.urljoin(
            fma_connect.settings.default_url, "/api/v1/models/1/register_client/"
        )
        mock_post.assert_called_with(
            url, headers={"CLIENT-UUID": "fake-uuid"}, timeout=10
        )
        self.assertTrue(client._is_registered)
        self.assertIsNone(client._last_model_aggregate)

    @mock.patch("requests.post")
    def test_send_update(self, mock_post):

        client = fma_connect.WebClient(federated_model_id=1)
        # validate server error
        mock_post.return_value.status_code = 403
        mock_post.return_value.json.return_value = {"detail": "unauthorized"}
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.send_update([1, 2, 3])

        # validate error, with uuid
        client._uuid = "fake-uuid"
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.send_update([1, 2, 3])

        # validate success
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"model_data": "test"}
        response = client.send_update([1, 2, 3])
        self.assertDictEqual({"model_data": "test"}, response)

        # validate success with base_aggregate set
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"model_data": "test"}
        response = client.send_update([1, 2, 3], base_aggregate=1)
        self.assertDictEqual({"model_data": "test"}, response)

    @mock.patch("fma_connect.WebClient.register")
    def test_uuid_property(self, mock_register):

        # test when no uuid assigned
        mock_register.return_value = "fake-uuid"
        client = fma_connect.WebClient(federated_model_id=1)
        self.assertEqual("fake-uuid", client.uuid)
        mock_register.assert_called()

        # test when uuid exists
        mock_register.reset_mock()
        client._uuid = "already-registered"
        self.assertEqual("already-registered", client.uuid)
        mock_register.assert_not_called()

    @mock.patch("requests.get")
    def test_check_for_new_model_aggregate(self, mock_get):
        client = fma_connect.WebClient(federated_model_id=1)

        # validate server error
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"detail": "unauthorized"}
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.check_for_new_model_aggregate()

        # validate error, with uuid
        client._uuid = "fake-uuid"
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"detail": "unauthorized"}
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.check_for_new_model_aggregate()

        # validate success, no update_after set
        self.assertIsNone(client._last_model_aggregate)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 1,  # should cause an update to last agg
            "results": [1, 4],
            "validation_score": 1.0,
        }
        response = client.check_for_new_model_aggregate()
        self.assertDictEqual(
            {"id": 1, "results": [1, 4], "validation_score": 1.0}, response
        )
        self.assertEqual(1, client._last_model_aggregate)

        # validate success, no values
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        response = client.check_for_new_model_aggregate()
        self.assertIsNone(response)
        self.assertEqual(1, client._last_model_aggregate)

        # validate success, update not new
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 1,
            "results": [1, 4],
            "validation_score": 6.7,
        }
        response = client.check_for_new_model_aggregate()
        self.assertIsNone(response)
        self.assertEqual(1, client._last_model_aggregate)

        # validate success, update is new
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 2,  # should cause an update to last agg
            "results": [2, 3],
            "validation_score": 3.8,
        }
        response = client.check_for_new_model_aggregate()
        self.assertDictEqual(
            {"id": 2, "results": [2, 3], "validation_score": 3.8}, response
        )
        self.assertEqual(2, client._last_model_aggregate)

        # validate success, update_after not new
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 3,  # should cause an update to last agg
            "results": [1, 4],
            "validation_score": 9.2,
        }
        response = client.check_for_new_model_aggregate(update_after=3)
        self.assertIsNone(response)
        self.assertEqual(3, client._last_model_aggregate)

        # validate success, update_after is new
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 2,  # should not cause an update to last agg
            "results": [2, 3],
            "validation_score": None,
        }
        response = client.check_for_new_model_aggregate(update_after=1)
        self.assertDictEqual(
            {"id": 2, "results": [2, 3], "validation_score": None}, response
        )
        self.assertEqual(3, client._last_model_aggregate)

    @mock.patch("requests.get")
    def test_get_current_artifact(self, mock_get):
        client = fma_connect.WebClient(federated_model_id=1)

        # validate server error
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"detail": "unauthorized"}
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.get_current_artifact()

        # validate error, with uuid
        client._uuid = "fake-uuid"
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"detail": "unauthorized"}
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.get_current_artifact()

        # validate success
        self.assertIsNone(client._last_model_aggregate)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 3,
            "values": [1, 2],
            "version": "1.0.0",
            "created_on": "2022-03-12T23:55:34.066180Z",
            "federated_model": 1,
        }
        expected_response = mock_get.return_value.json.return_value
        response = client.get_current_artifact()
        self.assertDictEqual(expected_response, response)

    @mock.patch("requests.get")
    def test_check_for_latest_model(self, mock_get):
        client = fma_connect.WebClient(federated_model_id=1)

        # validate server error
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"detail": "unauthorized"}
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.check_for_latest_model()

        # validate error, with uuid
        client._uuid = "fake-uuid"
        mock_get.return_value.status_code = 403
        mock_get.return_value.json.return_value = {"detail": "unauthorized"}
        with self.assertRaisesRegex(
            exceptions.APIException,
            r"An API error occurred \(status_code=403"
            r"\): {'detail': 'unauthorized'}",
        ):
            client.check_for_latest_model()

        # validate success w/ aggregate populated
        self.assertIsNone(client._last_model_aggregate)
        mock_get.return_value.json.return_value = {"values": [1, 2], "aggregate": 3}
        mock_get.return_value.status_code = 200
        expected_response = mock_get.return_value.json.return_value
        response = client.check_for_latest_model()
        self.assertDictEqual(expected_response, response)

        # validate success w/o aggregate populated
        client._last_model_aggregate = None
        # Setup for no model aggregate
        mock_get.return_value.json.return_value = {"values": [2, 5], "aggregate": None}
        expected_response = mock_get.return_value.json.return_value
        response = client.check_for_latest_model()
        self.assertDictEqual(expected_response, response)

        # validate success, no update_after set
        client._last_model_aggregate = None
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "aggregate": 1,  # should cause an update to last agg
            "values": [1, 4],
        }
        response = client.check_for_latest_model()
        self.assertDictEqual({"aggregate": 1, "values": [1, 4]}, response)
        self.assertEqual(1, client._last_model_aggregate)

        # validate success, no values
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        response = client.check_for_latest_model()
        self.assertIsNone(response)
        self.assertEqual(1, client._last_model_aggregate)

        # validate success, update not new
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "aggregate": 1,
            "values": [1, 4],
        }
        response = client.check_for_latest_model()
        self.assertIsNone(response)
        self.assertEqual(1, client._last_model_aggregate)

        # validate success, update is new
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "aggregate": 2,  # should cause an update to last agg
            "values": [2, 3],
        }
        response = client.check_for_latest_model()
        self.assertDictEqual({"aggregate": 2, "values": [2, 3]}, response)
        self.assertEqual(2, client._last_model_aggregate)

        # validate success, update_after not new
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "aggregate": 3,  # should cause an update to last agg
            "values": [1, 4],
        }
        response = client.check_for_latest_model(update_after=3)
        self.assertIsNone(response)
        self.assertEqual(3, client._last_model_aggregate)

        # validate success, update_after is new
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "aggregate": 2,  # should not cause an update to last agg
            "values": [2, 3],
        }
        response = client.check_for_latest_model(update_after=1)
        self.assertDictEqual({"aggregate": 2, "values": [2, 3]}, response)
        self.assertEqual(3, client._last_model_aggregate)
