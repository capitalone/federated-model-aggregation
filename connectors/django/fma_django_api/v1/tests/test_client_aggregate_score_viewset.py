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
class TestClientAggregateScoreViewSet(ClientMixin, LoginMixin, APITestCase):

    reverse_url = "client_aggregate_scores-list"
    fixtures = [
        "TaskQueue_User.json",
        "TaskQueue_client.json",
        "DjangoQ_Schedule.json",
        "TaskQueue_FederatedModel.json",
        "TaskQueue_ModelAggregate.json",
        "TaskQueue_ModelUpdate.json",
        "TaskQueue_ClientAggregateScore.json",
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
                "validation_results": {"f1_score": 0.8},
                "created_on": "2022-02-15T23:08:28.720000Z",
                "aggregate": 1,
            },
            {
                "id": 2,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "validation_results": {"prec": 0.25, "rec": 0.4, "skew": 0.6},
                "created_on": "2022-02-15T23:08:28.720000Z",
                "aggregate": 2,
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
                "id": 2,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "validation_results": {"prec": 0.25, "rec": 0.4, "skew": 0.6},
                "created_on": "2022-02-15T23:08:28.720000Z",
                "aggregate": 2,
            }
        ]
        self.assertEqual(200, response.status_code)
        self.assertCountEqual(expected_response, response.json())
        self.logout_client()

    def test_create(self, *mocks):
        baseurl = reverse(self.reverse_url)

        # validate unauthorized
        self._validate_unauthorized(baseurl, client_action=self.client.post)

        # validate authorized client
        self.login_client(client_json={"uuid": "ab359e5d-6991-4088-8815-a85d3e413c02"})
        create_data = {
            "client": "ab359e5d-6991-4088-8815-a85d3e413c02",
            "validation_results": {
                "f1_score": 0.8,
                "description": "This is a fake description",
            },
            "aggregate": 1,
        }

        response = self.client.post(baseurl, format="json", data=create_data)
        cleaned_response = response.json()

        # rather error show up on assert, hence `None`
        cleaned_response.pop("created_on", None)

        expected_response = create_data.copy()
        expected_response["id"] = 3
        expected_response["client"] = "ab359e5d-6991-4088-8815-a85d3e413c02"
        expected_response["aggregate"] = 1
        expected_response["validation_results"] = {
            "f1_score": 0.8,
            "description": "This is a fake description",
        }

        self.assertEqual(201, response.status_code)
        self.assertDictEqual(expected_response, cleaned_response)

        # validate authorized client (Non-unique failure)
        self.login_client(client_json={"uuid": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1"})

        create_data = {
            "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
            "validation_results": {"fake": 0.8},
            "aggregate": 1,
        }

        response = self.client.post(baseurl, format="json", data=create_data)
        cleaned_response = response.json()

        # Client already has a result registered for this aggregate so push fails
        expected_response = {
            "non_field_errors": ["The fields aggregate, client must make a unique set."]
        }
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected_response, cleaned_response)

        self.login_client(client_json={"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"})
        # test create w/ invalid schema
        create_data = {
            "client": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
            "validation_results": {
                "f1_score": 1.2,
                "description": "This is a fake description",
            },
            "aggregate": 1,
        }
        response = self.client.post(baseurl, format="json", data=create_data)
        cleaned_response = response.json()
        expected_response = {
            "results": [
                "results did not match the required schema: {}".format(
                    {
                        "properties": {
                            "f1_score": {"type": "number", "minimum": 0, "maximum": 1},
                            "description": {"type": "string"},
                        }
                    }
                )
            ]
        }
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected_response, cleaned_response)

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
            "validation_results": {"f1_score": 0.8},
            "created_on": "2022-02-15T23:08:28.720000Z",
            "aggregate": 1,
        }
        response_json = response.json()
        self.assertEqual(200, response.status_code)

        self.assertDictEqual(expected_response, response_json)

        # validate developer no access to models that they don't own
        self.login_user(user_json={"username": "non_admin"})
        response = self.client.get(baseurl + "1/", format="json")
        self.assertEqual(404, response.status_code)
        self.assertEqual({"detail": "Not found."}, response.json())

        # validate developer access to their own model
        response = self.client.get(baseurl + "2/", format="json")
        expected_response = {
            "id": 2,
            "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
            "validation_results": {"prec": 0.25, "rec": 0.4, "skew": 0.6},
            "created_on": "2022-02-15T23:08:28.720000Z",
            "aggregate": 2,
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

        # validate aggregate filtering
        queryurl = baseurl + "?aggregate=1"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 1,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "validation_results": {"f1_score": 0.8},
                "created_on": "2022-02-15T23:08:28.720000Z",
                "aggregate": 1,
            }
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

        # validate aggregate=2
        queryurl = baseurl + "?aggregate=2"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 2,
                "client": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                "validation_results": {"prec": 0.25, "rec": 0.4, "skew": 0.6},
                "created_on": "2022-02-15T23:08:28.720000Z",
                "aggregate": 2,
            }
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

    def test_pagination(self, *mocks):
        baseurl = reverse(self.reverse_url)

        # setting the page size to 2 and querying for page 1
        queryurl = baseurl + "?page_size=2&page=1"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.json()))

        # setting the page size to 1 and querying for page 1
        queryurl = baseurl + "?page_size=1&page=1"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))
