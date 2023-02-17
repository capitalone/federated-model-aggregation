from unittest import mock

from django.urls import reverse
from django.utils import timezone
from django_q.tasks import Schedule as djanog_q_Schedule
from rest_framework.authtoken import models as auth_models
from rest_framework.response import Response
from rest_framework.test import APITestCase

from fma_django import models
from fma_django_api import utils

from .utils import ClientMixin, LoginMixin


@mock.patch(
    "django.core.files.storage.FileSystemStorage.save", return_value="save_create"
)
class TestFederatedModelViewSet(ClientMixin, LoginMixin, APITestCase):

    reverse_url = "model-list"
    fixtures = [
        "TaskQueue_User.json",
        "TaskQueue_client.json",
        "DjangoQ_Schedule.json",
        "TaskQueue_FederatedModel.json",
        "TaskQueue_ModelAggregate.json",
        "TaskQueue_ModelArtifact.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # create artifact relation for model 1
        cls.fake_datetime = timezone.datetime(
            2022, 1, 1, 0, 0, 0, tzinfo=timezone.get_current_timezone()
        )
        fm_model = models.FederatedModel.objects.get(id=1)
        artifact_model = models.ModelArtifact.objects.get(id=3)
        fm_model.current_artifact = artifact_model
        with mock.patch(
            "django.utils.timezone.now", mock.Mock(return_value=cls.fake_datetime)
        ):
            fm_model.save()
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

        # validate client can't access
        self.login_client(client_json={"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"})

        response = client_action(baseurl, format="json")
        self.assertEqual(403, response.status_code)
        self.assertDictEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json(),
        )
        self.logout_client()

    def test_list(self, mock_save):

        baseurl = reverse(self.reverse_url)
        self._validate_unauthorized(baseurl, client_action=self.client.get)

        # validate authorized response given fixtures
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(baseurl, format="json")
        expected_response = [
            {
                "id": 2,
                "allow_aggregation": False,
                "name": "test-non-admin",
                "requirement": "all_clients",
                "requirement_args": None,
                "aggregator": "avg_values_if_data",
                "furthest_base_agg": None,
                "update_schema": None,
                "client_agg_results_schema": None,
                "created_on": "2022-12-24T23:08:28.693000Z",
                "last_modified": "2022-12-28T23:08:28.693000Z",
                "developer": 2,
                "current_artifact": None,
                "clients": [],
            },
            {
                "id": 3,
                "allow_aggregation": True,
                "name": "test-no-aggregate",
                "requirement": "all_clients",
                "requirement_args": None,
                "aggregator": "avg_values_if_data",
                "furthest_base_agg": None,
                "update_schema": {
                    "type": "array",
                    "prefixItems": [
                        {"type": "array", "minItems": 3, "maxItems": 3},
                        {"type": "array", "minItems": 3, "maxItems": 3},
                    ],
                    "items": False,
                },
                "client_agg_results_schema": None,
                "created_on": "2022-12-18T23:08:28.693000Z",
                "last_modified": "2022-12-19T23:08:28.693000Z",
                "developer": 2,
                "current_artifact": None,
                "clients": ["cbb6025f-c15c-4e90-b3fb-85626f7a79f1"],
            },
            {
                "id": 1,
                "allow_aggregation": True,
                "requirement": "require_x_updates",
                "name": "test",
                "requirement_args": [3],
                "aggregator": "avg_values_if_data",
                "furthest_base_agg": None,
                "update_schema": {
                    "type": "array",
                    "prefixItems": [
                        {"type": "array", "minItems": 3, "maxItems": 3},
                        {"type": "array", "minItems": 3, "maxItems": 3},
                    ],
                    "items": False,
                },
                "client_agg_results_schema": {
                    "properties": {
                        "f1_score": {"type": "number", "minimum": 0, "maximum": 1},
                        "description": {"type": "string"},
                    }
                },
                "created_on": "2022-12-15T23:08:28.693000Z",
                "last_modified": "2022-01-01T00:00:00Z",
                "developer": 1,
                "current_artifact": 3,
                "clients": [
                    "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
                    "ab359e5d-6991-4088-8815-a85d3e413c02",
                    "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                ],
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

    def test_create(self, mock_save):
        baseurl = reverse(self.reverse_url)

        # validate unauthorized
        self._validate_unauthorized(baseurl, client_action=self.client.post)

        # validate authorized admin
        self.login_user(user_json={"username": "admin"})
        create_data = {
            "name": "create-test",
            "aggregator": "avg_values_if_data",
            "developer": 1,
            "initial_model": [1, 2, 3],
            "update_schema": {"test": 1},
            "clients": [
                "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
                "ab359e5d-6991-4088-8815-a85d3e413c02",
            ],
        }
        with mock.patch(
            "django.utils.timezone.now", mock.Mock(return_value=self.fake_datetime)
        ):
            response = self.client.post(baseurl, format="json", data=create_data)
        cleaned_response = response.json()

        expected_response = create_data.copy()
        expected_response.pop("initial_model", None)
        expected_response["id"] = 4
        expected_response["furthest_base_agg"] = None
        expected_response["allow_aggregation"] = False  # default False
        expected_response["requirement_args"] = None
        expected_response["requirement"] = ""
        expected_response["current_artifact"] = 4
        expected_response["created_on"] = "2022-01-01T00:00:00Z"
        expected_response["last_modified"] = "2022-01-01T00:00:00Z"
        expected_response["client_agg_results_schema"] = None
        self.assertEqual(201, response.status_code, response.json())
        self.assertDictEqual(expected_response, cleaned_response)

        # also assert the task is created in the db
        scheduled_model = djanog_q_Schedule.objects.filter(
            name="4 - create-test - Scheduled Aggregator"
        ).first()
        self.assertIsNotNone(
            scheduled_model, "Validating if schedule was created with the model."
        )
        self.logout_user()

        # test developer
        self.login_user(user_json={"username": "non_admin"})
        create_data = {
            "name": "non_admin create-test",
            "allow_aggregation": True,
            "aggregator": "avg_values_if_data",
            "developer": 2,
            "update_schema": None,
            "clients": [
                "ab359e5d-6991-4088-8815-a85d3e413c02",
                "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
            ],
        }

        with mock.patch(
            "django.utils.timezone.now", mock.Mock(return_value=self.fake_datetime)
        ):
            response = self.client.post(baseurl, format="json", data=create_data)
        cleaned_response = response.json()

        expected_response = create_data.copy()
        expected_response["id"] = 5
        expected_response["furthest_base_agg"] = None
        expected_response["requirement_args"] = None
        expected_response["requirement"] = ""
        expected_response["current_artifact"] = None
        expected_response["created_on"] = "2022-01-01T00:00:00Z"
        expected_response["last_modified"] = "2022-01-01T00:00:00Z"
        expected_response["client_agg_results_schema"] = None

        self.assertEqual(201, response.status_code)
        self.assertDictEqual(expected_response, cleaned_response)

        # also assert the task is created in the db
        scheduled_model = djanog_q_Schedule.objects.filter(
            name="5 - non_admin create-test - Scheduled Aggregator"
        ).first()
        self.assertIsNotNone(
            scheduled_model, "Validating if schedule was created with the model."
        )

        # validate furthest_base_agg fails if not > 1
        create_data = {
            "name": "test-furthest-base-agg",
            "aggregator": "avg_values_if_data",
            "developer": 2,
            "initial_model": [1, 2, 3],
            "update_schema": {"test": 1},
            "furthest_base_agg": -1,
        }
        response = self.client.post(baseurl, format="json", data=create_data)
        self.assertEqual(400, response.status_code)
        cleaned_response = response.json()
        self.assertDictEqual(
            {"furthest_base_agg": ["Ensure this value is greater than or equal to 1."]},
            cleaned_response,
        )

        # validate furthest_base_agg success if  >= 1
        create_data = {
            "name": "test-furthest-base-agg",
            "aggregator": "avg_values_if_data",
            "developer": 2,
            "initial_model": [1, 2, 3],
            "update_schema": {"test": 1},
            "furthest_base_agg": 3,
        }
        response = self.client.post(baseurl, format="json", data=create_data)
        self.assertEqual(201, response.status_code)
        cleaned_response = response.json()
        self.assertEqual(3, cleaned_response.get("furthest_base_agg", None))
        self.logout_user()

        # TODO: don't allow developer to set users, can force this in the
        # queryset for a user

    def test_get(self, mock_save):
        baseurl = reverse(self.reverse_url)

        # validate unauthorized
        self._validate_unauthorized(baseurl + "1/", client_action=self.client.get)

        # validate admin access to both
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(baseurl + "1/", format="json")
        expected_response = {
            "id": 1,
            "allow_aggregation": True,
            "name": "test",
            "requirement": "require_x_updates",
            "requirement_args": [3],
            "aggregator": "avg_values_if_data",
            "furthest_base_agg": None,
            "update_schema": {
                "type": "array",
                "prefixItems": [
                    {"type": "array", "minItems": 3, "maxItems": 3},
                    {"type": "array", "minItems": 3, "maxItems": 3},
                ],
                "items": False,
            },
            "client_agg_results_schema": {
                "properties": {
                    "f1_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "description": {"type": "string"},
                }
            },
            "created_on": "2022-12-15T23:08:28.693000Z",
            "last_modified": "2022-01-01T00:00:00Z",
            "developer": 1,
            "current_artifact": 3,
            "clients": [
                "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
                "ab359e5d-6991-4088-8815-a85d3e413c02",
                "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
            ],
        }
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_response, response.json())

        response = self.client.get(baseurl + "2/", format="json")
        expected_response = {
            "id": 2,
            "allow_aggregation": False,
            "name": "test-non-admin",
            "requirement": "all_clients",
            "requirement_args": None,
            "aggregator": "avg_values_if_data",
            "furthest_base_agg": None,
            "update_schema": None,
            "client_agg_results_schema": None,
            "created_on": "2022-12-24T23:08:28.693000Z",
            "last_modified": "2022-12-28T23:08:28.693000Z",
            "developer": 2,
            "current_artifact": None,
            "clients": [],
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
        response = self.client.get(baseurl + "2/", format="json")
        expected_response = {
            "id": 2,
            "allow_aggregation": False,
            "name": "test-non-admin",
            "requirement": "all_clients",
            "requirement_args": None,
            "aggregator": "avg_values_if_data",
            "furthest_base_agg": None,
            "update_schema": None,
            "client_agg_results_schema": None,
            "created_on": "2022-12-24T23:08:28.693000Z",
            "last_modified": "2022-12-28T23:08:28.693000Z",
            "developer": 2,
            "current_artifact": None,
            "clients": [],
        }
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_response, response.json())

    def test_register_client(self, mock_save):

        baseurl = reverse(self.reverse_url)
        url = baseurl + "1/register_client/"

        # validate get doesn't work
        response = self.client.get(url, format="json")
        self.assertEqual(405, response.status_code)
        self.assertDictEqual({"detail": 'Method "GET" not allowed.'}, response.json())

        # validate bad uuid doesn't work
        response = self.client.post(url, format="json", HTTP_CLIENT_UUID="test")
        self.assertEqual(403, response.status_code)
        self.assertDictEqual({"detail": '"test" is not a valid UUID.'}, response.json())

        # validate current UUID
        response = self.client.post(
            url, format="json", HTTP_CLIENT_UUID="531580e6-ce6c-4f01-a5aa-9ed7af5ee768"
        )
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(
            {"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"}, response.json()
        )

        # validate make new UUID
        fake_uuid = "000000e6-ce6c-4f01-a5aa-9ed7af5ee768"
        with mock.patch(
            "fma_django.models.Client.uuid.field.get_default",
            return_value=fake_uuid,
        ):
            response = self.client.post(url, format="json")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({"uuid": fake_uuid}, response.json())

        # validate new is reusable
        url = baseurl + "2/register_client/"
        response = self.client.post(url, format="json", HTTP_CLIENT_UUID=fake_uuid)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({"uuid": fake_uuid}, response.json())

        # validate devleoper can make a client
        url = baseurl + "2/register_client/"
        self.login_user(user_json={"username": "non_admin"})
        fake_uuid = "111111e6-ce6c-4f01-a5aa-9ed7af5ee768"
        with mock.patch(
            "fma_django.models.Client.uuid.field.get_default",
            return_value=fake_uuid,
        ):
            response = self.client.post(url, format="json")
        self.assertEqual(200, response.status_code)
        self.assertDictEqual({"uuid": fake_uuid}, response.json())
        self.logout_user()

    def test_get_latest_aggregate(self, mock_save):

        baseurl = reverse(self.reverse_url)
        url = baseurl + "1/get_latest_aggregate/"

        # validate current UUID
        self.login_client(client_json={"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"})
        response = self.client.get(url, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {
            "id": 1,
            "federated_model": 1,
            "result": "/mediafiles/fake/path/model_aggregate/1",
            "validation_score": 1.0,
            "created_on": "2023-01-13T23:08:28.712000Z",
            "lft": 1,
            "rght": 2,
            "tree_id": 0,
            "level": 0,
            "parent": None,
        }
        self.assertDictEqual(expected_response, response.json())

        # validate client cannot get from model with not registered
        url = baseurl + "2/get_latest_aggregate/"
        response = self.client.get(url, format="json")
        self.assertEqual(403, response.status_code)
        self.assertDictEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json(),
        )
        self.logout_client()

        # validate developer has access to own
        self.login_user(user_json={"username": "non_admin"})
        url = baseurl + "2/get_latest_aggregate/"
        response = self.client.get(url, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {
            "id": 2,
            "federated_model": 2,
            "result": "/mediafiles/fake/path/model_aggregate/2",
            "validation_score": None,
            "created_on": "2023-01-20T23:08:28.712000Z",
            "lft": 1,
            "rght": 2,
            "tree_id": 1,
            "level": 0,
            "parent": None,
        }

        self.assertDictEqual(expected_response, response.json())

        # validate developer cannot get from model of another
        url = baseurl + "1/get_latest_aggregate/"
        response = self.client.get(url, format="json")
        self.assertEqual(404, response.status_code)
        self.assertDictEqual({"detail": "Not found."}, response.json())

        # validate when model doesn't have an aggregate
        models.ModelAggregate.objects.filter(federated_model=2).delete()
        url = baseurl + "2/get_latest_aggregate/"
        response = self.client.get(url, format="json")
        expected_response = {}
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

    def test_get_current_artifact(self, mock_save):
        baseurl = reverse(self.reverse_url)
        url = baseurl + "1/get_current_artifact/"

        # validate current UUID
        self.login_client(client_json={"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"})
        response = self.client.get(url, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {
            "id": 3,
            "federated_model": 1,
            "values": "/mediafiles/fake/path/model_artifact/1",
            "version": "1.0.0",
            "created_on": "2022-12-12T23:55:34.066000Z",
        }
        self.assertDictEqual(expected_response, response.json())

        # validate client cannot get from model with not registered
        url = baseurl + "2/get_current_artifact/"
        response = self.client.get(url, format="json")
        self.assertEqual(403, response.status_code)
        self.assertDictEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json(),
        )
        self.logout_client()

        # validate developer has access to own, also check returns null if empty
        self.login_user(user_json={"username": "non_admin"})
        url = baseurl + "2/get_current_artifact/"
        response = self.client.get(url, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {}
        self.assertDictEqual(expected_response, response.json())

        # validate developer cannot get from model of another
        url = baseurl + "1/get_current_artifact/"
        response = self.client.get(url, format="json")
        self.assertEqual(404, response.status_code)
        self.assertDictEqual({"detail": "Not found."}, response.json())
        self.logout_user()

    def test_get_latest_model(self, mock_save):
        baseurl = reverse(self.reverse_url)

        # validate client cannot get from model with not registered
        url = baseurl + "2/get_latest_model/"
        response = self.client.get(url, format="json")
        self.assertEqual(401, response.status_code)
        self.assertDictEqual(
            {"detail": "Authentication credentials were not provided."}, response.json()
        )

        # validate current UUID
        url = baseurl + "1/get_latest_model/"
        self.login_client(client_json={"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"})
        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open"
        ) as mock_load:
            # Turn aggregation results into file
            mock_load.return_value = utils.create_model_file([0.5, 1, 2])
            response = self.client.get(url, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {"values": [0.5, 1, 2], "aggregate": 1}
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

        # validate developer cannot get from model of another
        self.login_user(user_json={"username": "non_admin"})
        url = baseurl + "1/get_latest_model/"
        response = self.client.get(url, format="json")
        self.assertEqual(404, response.status_code)
        self.logout_user()

        # validate when model doesn't have an aggregate
        self.login_user(user_json={"username": "admin"})
        models.ModelAggregate.objects.filter(federated_model=1).delete()
        url = baseurl + "1/get_latest_model/"
        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open"
        ) as mock_load:
            # Turn aggregation results into file
            mock_load.return_value = utils.create_model_file([0.5, 1, 2])
            response = self.client.get(url, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {"values": [0.5, 1, 2], "aggregate": None}
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

        # validate developer has access to own, also check returns null if
        # both aggregate and artifact are empty
        models.ModelAggregate.objects.filter(federated_model=2).delete()
        models.ModelArtifact.objects.filter(federated_model=2).delete()
        self.login_user(user_json={"username": "non_admin"})
        url = baseurl + "2/get_latest_model/"
        response = self.client.get(url, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {}
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

    @mock.patch("rest_framework.mixins.ListModelMixin.list")
    def test_token_login(self, mock_list, mock_save):
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

        # validate allow_aggregation=True
        queryurl = baseurl + "?allow_aggregation=True"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 3,
                "allow_aggregation": True,
                "name": "test-no-aggregate",
                "requirement": "all_clients",
                "requirement_args": None,
                "aggregator": "avg_values_if_data",
                "furthest_base_agg": None,
                "update_schema": {
                    "type": "array",
                    "prefixItems": [
                        {"type": "array", "minItems": 3, "maxItems": 3},
                        {"type": "array", "minItems": 3, "maxItems": 3},
                    ],
                    "items": False,
                },
                "client_agg_results_schema": None,
                "created_on": "2022-12-18T23:08:28.693000Z",
                "last_modified": "2022-12-19T23:08:28.693000Z",
                "developer": 2,
                "current_artifact": None,
                "clients": ["cbb6025f-c15c-4e90-b3fb-85626f7a79f1"],
            },
            {
                "id": 1,
                "allow_aggregation": True,
                "requirement": "require_x_updates",
                "name": "test",
                "requirement_args": [3],
                "aggregator": "avg_values_if_data",
                "furthest_base_agg": None,
                "update_schema": {
                    "type": "array",
                    "prefixItems": [
                        {"type": "array", "minItems": 3, "maxItems": 3},
                        {"type": "array", "minItems": 3, "maxItems": 3},
                    ],
                    "items": False,
                },
                "client_agg_results_schema": {
                    "properties": {
                        "f1_score": {"type": "number", "minimum": 0, "maximum": 1},
                        "description": {"type": "string"},
                    }
                },
                "created_on": "2022-12-15T23:08:28.693000Z",
                "last_modified": "2022-01-01T00:00:00Z",
                "developer": 1,
                "current_artifact": 3,
                "clients": [
                    "531580e6-ce6c-4f01-a5aa-9ed7af5ee768",
                    "ab359e5d-6991-4088-8815-a85d3e413c02",
                    "cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
                ],
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

        # validate allow_aggregation=False
        queryurl = baseurl + "?allow_aggregation=false"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 2,
                "allow_aggregation": False,
                "name": "test-non-admin",
                "requirement": "all_clients",
                "requirement_args": None,
                "aggregator": "avg_values_if_data",
                "furthest_base_agg": None,
                "update_schema": None,
                "client_agg_results_schema": None,
                "created_on": "2022-12-24T23:08:28.693000Z",
                "last_modified": "2022-12-28T23:08:28.693000Z",
                "developer": 2,
                "current_artifact": None,
                "clients": [],
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
