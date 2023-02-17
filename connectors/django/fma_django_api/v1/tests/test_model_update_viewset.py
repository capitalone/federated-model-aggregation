from unittest import mock

from django.urls import reverse
from rest_framework.authtoken import models as auth_models
from rest_framework.response import Response
from rest_framework.test import APITestCase

from fma_django import models

from .utils import ClientMixin, LoginMixin


@mock.patch(
    "django.core.files.storage.FileSystemStorage.save", return_value="save_create"
)
class TestModelUpdateViewSet(ClientMixin, LoginMixin, APITestCase):

    reverse_url = "model_update-list"
    fixtures = [
        "TaskQueue_User.json",
        "TaskQueue_client.json",
        "DjangoQ_Schedule.json",
        "TaskQueue_FederatedModel.json",
        "TaskQueue_ModelAggregate.json",
        "TaskQueue_ModelUpdate.json",
    ]

    def setUp(self):
        for user in models.User.objects.all():
            auth_models.Token.objects.get_or_create(user=user)

    def _validate_unauthorized(self, baseurl, client_action, request_json=None):
        if request_json is None:
            request_json = {}
        # validate unauthorized, no one logged in
        response = client_action(baseurl, format="json")
        self.assertEqual(401, response.status_code)
        self.assertDictEqual(
            {"detail": "Authentication credentials were not provided."}, response.json()
        )

        # validate invalid uuid client can't access
        response = client_action(
            baseurl, format="json", HTTP_CLIENT_UUID="not-a-client"
        )
        self.assertEqual(401, response.status_code)
        self.assertDictEqual(
            {"detail": '"not-a-client" is not a valid UUID.'}, response.json()
        )

        # validate non-existent client can't access
        response = client_action(
            baseurl,
            format="json",
            HTTP_CLIENT_UUID="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        )
        self.assertEqual(401, response.status_code)
        self.assertDictEqual({"detail": "Invalid UUID"}, response.json())

    def test_list(self, *mocks):

        baseurl = reverse(self.reverse_url)
        self._validate_unauthorized(baseurl, client_action=self.client.get)

        # validate authorized response given fixtures
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(baseurl, format="json")

        expected_response = [
            {
                "id": 1,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/1",
                "status": 2,
                "created_on": "2022-12-15T23:08:28.720000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 2,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/2",
                "status": 2,
                "created_on": "2023-01-10T23:10:33.720000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 3,
                "client": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/3",
                "status": 2,
                "created_on": "2023-01-16T23:17:35.480000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 4,
                "client": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/4",
                "status": 3,
                "created_on": "2022-02-17T17:58:13.819000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 5,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 2,
                "data": "http://testserver/mediafiles/fake/path/model_updates/5",
                "status": 0,
                "created_on": "2022-02-17T17:58:44.441000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 6,
                "client": "ab359e5d-6991-4088-8815-a85d3e413c02",
                "federated_model": 2,
                "data": "http://testserver/mediafiles/fake/path/model_updates/6",
                "status": 0,
                "created_on": "2022-02-28T00:36:54.803000Z",
                "base_aggregate": 2,
                "applied_aggregate": None,
            },
            {
                "id": 7,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 3,
                "data": "http://testserver/mediafiles/fake/path/model_updates/7",
                "status": 0,
                "created_on": "2022-12-26T01:12:55.467000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 8,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 3,
                "data": "http://testserver/mediafiles/fake/path/model_updates/8",
                "status": 0,
                "created_on": "2022-12-08T13:22:24.557000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertCountEqual(expected_response, response.json())
        self.logout_user()

        # validate developer only sees their own
        self.login_user(user_json={"username": "non_admin"})
        response = self.client.get(baseurl, format="json")
        expected_response = [
            {
                "id": 5,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 2,
                "data": "http://testserver/mediafiles/fake/path/model_updates/5",
                "status": 0,
                "created_on": "2022-02-17T17:58:44.441000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 6,
                "client": "ab359e5d-6991-4088-8815-a85d3e413c02",
                "federated_model": 2,
                "data": "http://testserver/mediafiles/fake/path/model_updates/6",
                "status": 0,
                "created_on": "2022-02-28T00:36:54.803000Z",
                "base_aggregate": 2,
                "applied_aggregate": None,
            },
            {
                "id": 7,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 3,
                "data": "http://testserver/mediafiles/fake/path/model_updates/7",
                "status": 0,
                "created_on": "2022-12-26T01:12:55.467000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 8,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 3,
                "data": "http://testserver/mediafiles/fake/path/model_updates/8",
                "status": 0,
                "created_on": "2022-12-08T13:22:24.557000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertCountEqual(expected_response, response.json())
        self.logout_user()

        # validate client view
        self.login_client(client_json={"uuid": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1"})
        response = self.client.get(baseurl, format="json")
        expected_response = [
            {
                "id": 1,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/1",
                "created_on": "2022-12-15T23:08:28.720000Z",
                "base_aggregate": None,
            },
            {
                "id": 2,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/2",
                "created_on": "2023-01-10T23:10:33.720000Z",
                "base_aggregate": None,
            },
            {
                "id": 5,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 2,
                "data": "http://testserver/mediafiles/fake/path/model_updates/5",
                "created_on": "2022-02-17T17:58:44.441000Z",
                "base_aggregate": None,
            },
            {
                "id": 7,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 3,
                "data": "http://testserver/mediafiles/fake/path/model_updates/7",
                "created_on": "2022-12-26T01:12:55.467000Z",
                "base_aggregate": None,
            },
            {
                "id": 8,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 3,
                "data": "http://testserver/mediafiles/fake/path/model_updates/8",
                "created_on": "2022-12-08T13:22:24.557000Z",
                "base_aggregate": None,
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertCountEqual(expected_response, response.json())
        self.logout_client()

    def test_create(self, *mocks):
        baseurl = reverse(self.reverse_url)

        # validate unauthorized
        self._validate_unauthorized(baseurl, client_action=self.client.post)
        # validate client can't set client, status
        self.login_client(client_json={"uuid": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1"})
        create_data = {
            "client": "aab6025f-c15c-4e90-b3fb-85626f7a79f1",
            "data": [[1, 5, 2], [2, 3, 4]],
            "federated_model": 1,
            "base_aggregate": None,
        }
        with mock.patch(
            "django.core.files.storage.FileSystemStorage.save"
        ) as mock_save:
            mock_save.return_value = "created data"
            response = self.client.post(baseurl, format="json", data=create_data)
        print(response)
        cleaned_response = response.json()

        # rather error show up on assert, hence `None`
        cleaned_response.pop("created_on", None)
        cleaned_response.pop("last_modified", None)

        expected_response = create_data.copy()
        expected_response["id"] = 9
        expected_response["client"] = "cbb6025f-c15c-4e90-b3fb-85626f7a79f1"
        expected_response["data"] = "http://testserver/mediafiles/created%20data"
        expected_response["base_aggregate"] = None

        self.assertEqual(201, response.status_code)
        self.assertDictEqual(expected_response, cleaned_response)

        # validate authorized client
        self.login_client(client_json={"uuid": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1"})
        create_data = {
            "data": [[1, 5, 2], [2, 3, 4]],
            "federated_model": 1,
        }
        with mock.patch(
            "django.core.files.storage.FileSystemStorage.save"
        ) as mock_save:
            mock_save.return_value = "created data"
            response = self.client.post(baseurl, format="json", data=create_data)
        cleaned_response = response.json()

        # rather error show up on assert, hence `None`
        cleaned_response.pop("created_on", None)
        cleaned_response.pop("last_modified", None)

        expected_response = create_data.copy()
        expected_response["id"] = 10
        expected_response["client"] = "cbb6025f-c15c-4e90-b3fb-85626f7a79f1"
        expected_response["base_aggregate"] = None
        expected_response["data"] = "http://testserver/mediafiles/created%20data"

        self.assertEqual(201, response.status_code)
        self.assertDictEqual(expected_response, cleaned_response)

        # test create w/ invalid schema
        create_data = {
            "data": [[1, 5], [2, 3]],
            "federated_model": 1,
        }
        response = self.client.post(baseurl, format="json", data=create_data)
        cleaned_response = response.json()
        expected_response = {
            "data": [
                "data did not match the required schema: {}".format(
                    {
                        "type": "array",
                        "prefixItems": [
                            {"type": "array", "minItems": 3, "maxItems": 3},
                            {"type": "array", "minItems": 3, "maxItems": 3},
                        ],
                        "items": False,
                    }
                )
            ]
        }
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected_response, cleaned_response)

        # TODO: create test to not allow non-registered clients

    def test_get(self, *mocks):
        baseurl = reverse(self.reverse_url)

        # validate unauthorized
        self._validate_unauthorized(baseurl + "1/", client_action=self.client.get)

        # validate admin access to both
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(baseurl + "1/", format="json")

        expected_response = {
            "id": 1,
            "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
            "federated_model": 1,
            "data": "http://testserver/mediafiles/fake/path/model_updates/1",
            "status": 2,
            "created_on": "2022-12-15T23:08:28.720000Z",
            "base_aggregate": None,
            "applied_aggregate": None,
        }
        response_json = response.json()
        self.assertEqual(200, response.status_code)

        self.assertDictEqual(expected_response, response_json)

        response = self.client.get(baseurl + "2/", format="json")
        expected_response = {
            "id": 2,
            "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
            "federated_model": 1,
            "data": "http://testserver/mediafiles/fake/path/model_updates/2",
            "status": 2,
            "created_on": "2023-01-10T23:10:33.720000Z",
            "base_aggregate": None,
            "applied_aggregate": None,
        }
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

        # validate developer no access to models that they don't own
        self.login_user(user_json={"username": "non_admin"})
        response = self.client.get(baseurl + "1/", format="json")
        self.assertEqual(404, response.status_code)
        self.assertEqual({"detail": "Not found."}, response.json())

        # validate developer access to their own model
        response = self.client.get(baseurl + "5/", format="json")
        expected_response = {
            "id": 5,
            "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
            "federated_model": 2,
            "data": "http://testserver/mediafiles/fake/path/model_updates/5",
            "status": 0,
            "created_on": "2022-02-17T17:58:44.441000Z",
            "base_aggregate": None,
            "applied_aggregate": None,
        }
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_response, response.json())

    @mock.patch("rest_framework.mixins.ListModelMixin.list")
    def test_token_login(self, mock_list, *mocks):
        # validate get using auth token
        baseurl = reverse(self.reverse_url)

        user_json = {"username": "non_admin"}
        mock_list.return_value = Response({"detail": "successful API Call"})
        self.user_token_login(user_json=user_json)

        _ = self.client.get(baseurl)
        params = mock_list.call_args
        mock_list.assert_called_once()
        self.assertEqual(self.user, params[0][0].user)

        self.user_token_logout()

    def test_filters(self, *mocks):
        baseurl = reverse(self.reverse_url)

        # validate federated_model filtering
        queryurl = baseurl + "?federated_model=1"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 3,
                "client": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/3",
                "status": 2,
                "created_on": "2023-01-16T23:17:35.480000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 2,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/2",
                "status": 2,
                "created_on": "2023-01-10T23:10:33.720000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 1,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/1",
                "status": 2,
                "created_on": "2022-12-15T23:08:28.720000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 4,
                "client": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
                "federated_model": 1,
                "data": "http://testserver/mediafiles/fake/path/model_updates/4",
                "status": 3,
                "created_on": "2022-02-17T17:58:13.819000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

        # validate federate_model=2
        queryurl = baseurl + "?federated_model=2"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 6,
                "client": "ab359e5d-6991-4088-8815-a85d3e413c02",
                "federated_model": 2,
                "data": "http://testserver/mediafiles/fake/path/model_updates/6",
                "status": 0,
                "created_on": "2022-02-28T00:36:54.803000Z",
                "base_aggregate": 2,
                "applied_aggregate": None,
            },
            {
                "id": 5,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 2,
                "data": "http://testserver/mediafiles/fake/path/model_updates/5",
                "status": 0,
                "created_on": "2022-02-17T17:58:44.441000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

        # validate federate_model=2
        queryurl = baseurl + "?status=0"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 7,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 3,
                "data": "http://testserver/mediafiles/fake/path/model_updates/7",
                "status": 0,
                "created_on": "2022-12-26T01:12:55.467000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 8,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 3,
                "data": "http://testserver/mediafiles/fake/path/model_updates/8",
                "status": 0,
                "created_on": "2022-12-08T13:22:24.557000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
            {
                "id": 6,
                "data": "http://testserver/mediafiles/fake/path/model_updates/6",
                "status": 0,
                "created_on": "2022-02-28T00:36:54.803000Z",
                "client": "ab359e5d-6991-4088-8815-a85d3e413c02",
                "federated_model": 2,
                "base_aggregate": 2,
                "applied_aggregate": None,
            },
            {
                "id": 5,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "federated_model": 2,
                "data": "http://testserver/mediafiles/fake/path/model_updates/5",
                "status": 0,
                "created_on": "2022-02-17T17:58:44.441000Z",
                "base_aggregate": None,
                "applied_aggregate": None,
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

    def test_pagination(self, *mocks):
        baseurl = reverse(self.reverse_url)

        # setting the page size to 4 and querying for page 2
        queryurl = baseurl + "?page_size=4&page=2"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(4, len(response.json()))

        # setting the page size to 2 and querying for page 2
        queryurl = baseurl + "?page_size=2&page=2"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.json()))
