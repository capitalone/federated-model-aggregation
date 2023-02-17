from unittest import mock

from django.urls import reverse
from rest_framework.authtoken import models as auth_models
from rest_framework.response import Response
from rest_framework.test import APITestCase

from fma_django import models
from fma_django_api import utils

from .utils import ClientMixin, LoginMixin


class TestModelAggregateViewSet(ClientMixin, LoginMixin, APITestCase):

    reverse_url = "model_aggregate-list"
    fixtures = [
        "TaskQueue_User.json",
        "TaskQueue_client.json",
        "DjangoQ_Schedule.json",
        "TaskQueue_FederatedModel.json",
        "TaskQueue_ModelAggregate.json",
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

        # validate non-existent client can't access
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

        # validate client user can only view
        if client_action != self.client.get:
            response = client_action(
                baseurl,
                format="json",
                HTTP_CLIENT_UUID="cbb6025f-c15c-4e90-b3fb-85626f7a79f1",
            )
            self.assertEqual(403, response.status_code)
            self.assertDictEqual(
                {"detail": "You do not have permission to perform this action."},
                response.json(),
            )

    def test_list(self):

        baseurl = reverse(self.reverse_url)
        self._validate_unauthorized(baseurl, client_action=self.client.get)

        # validate authorized response given fixtures
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(baseurl, format="json")
        expected_response = [
            {
                "id": 2,
                "federated_model": 2,
                "result": "http://testserver/mediafiles/fake/path/model_aggregate/2",
                "validation_score": None,
                "created_on": "2023-01-20T23:08:28.712000Z",
                "parent": None,
                "level": 0,
                "lft": 1,
                "rght": 2,
                "tree_id": 1,
            },
            {
                "id": 1,
                "federated_model": 1,
                "result": "http://testserver/mediafiles/fake/path/model_aggregate/1",
                "validation_score": 1.0,
                "created_on": "2023-01-13T23:08:28.712000Z",
                "parent": None,
                "level": 0,
                "lft": 1,
                "rght": 2,
                "tree_id": 0,
            },
        ]

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())
        self.logout_user()

        # validate developer only sees their own
        self.login_user(user_json={"username": "non_admin"})
        response = self.client.get(baseurl, format="json")
        expected_response = [
            {
                "id": 2,
                "federated_model": 2,
                "result": "http://testserver/mediafiles/fake/path/model_aggregate/2",
                "validation_score": None,
                "created_on": "2023-01-20T23:08:28.712000Z",
                "parent": None,
                "level": 0,
                "lft": 1,
                "rght": 2,
                "tree_id": 1,
            }
        ]
        self.assertEqual(200, response.status_code)

        self.assertEqual(expected_response, response.json())
        self.logout_user()

        # validate client view, only model it has access to
        self.login_client(client_json={"uuid": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1"})
        response = self.client.get(baseurl, format="json")
        expected_response = [
            {
                "id": 1,
                "federated_model": 1,
                "result": "http://testserver/mediafiles/fake/path/model_aggregate/1",
                "validation_score": 1.0,
                "created_on": "2023-01-13T23:08:28.712000Z",
                "parent": None,
                "level": 0,
                "lft": 1,
                "rght": 2,
                "tree_id": 0,
            }
        ]

        self.assertEqual(200, response.status_code)

        self.assertEqual(expected_response, response.json())
        self.logout_client()

    def test_create(self):
        baseurl = reverse(self.reverse_url)

        # validate unauthorized
        self._validate_unauthorized(baseurl, client_action=self.client.post)

    def test_get(self):
        baseurl = reverse(self.reverse_url)

        # validate unauthorized
        self._validate_unauthorized(baseurl + "1/", client_action=self.client.get)

        # validate admin access to both
        self.login_user(user_json={"username": "admin"})
        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open"
        ) as mock_load:
            # Turn aggregation results into file
            mock_load.return_value = utils.create_model_file([5, 2, 3])
            response = self.client.get(baseurl + "1/", format="json")
        expected_response = {
            "id": 1,
            "federated_model": 1,
            "result": [5, 2, 3],
            "validation_score": 1.0,
            "created_on": "2023-01-13T23:08:28.712000Z",
            "parent": None,
            "level": 0,
            "lft": 1,
            "rght": 2,
            "tree_id": 0,
        }
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_response, response.json())

        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open"
        ) as mock_load:
            # Turn aggregation results into file
            mock_load.return_value = utils.create_model_file([1, 2, 4])
            response = self.client.get(baseurl + "2/", format="json")
        expected_response = {
            "id": 2,
            "federated_model": 2,
            "result": [1, 2, 4],
            "validation_score": None,
            "created_on": "2023-01-20T23:08:28.712000Z",
            "parent": None,
            "level": 0,
            "lft": 1,
            "rght": 2,
            "tree_id": 1,
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
        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open"
        ) as mock_load:
            # Turn aggregation results into file
            mock_load.return_value = utils.create_model_file([1, 2, 4])
            response = self.client.get(baseurl + "2/", format="json")
        expected_response = {
            "id": 2,
            "federated_model": 2,
            "result": [1, 2, 4],
            "validation_score": None,
            "created_on": "2023-01-20T23:08:28.712000Z",
            "parent": None,
            "level": 0,
            "lft": 1,
            "rght": 2,
            "tree_id": 1,
        }
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

        # validate client has no access to unregistered models
        self.login_client(client_json={"uuid": "cbb6025f-c15c-4e90-b3fb-85626f7a79f1"})
        response = self.client.get(baseurl + "2/", format="json")
        self.assertEqual(404, response.status_code)
        self.assertEqual({"detail": "Not found."}, response.json())

        # validate client has access to their registered models
        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open"
        ) as mock_load:
            # Turn aggregation results into file
            mock_load.return_value = utils.create_model_file([5, 2, 3])
            response = self.client.get(baseurl + "1/", format="json")
        expected_response = {
            "id": 1,
            "federated_model": 1,
            "result": [5, 2, 3],
            "validation_score": 1.0,
            "created_on": "2023-01-13T23:08:28.712000Z",
            "parent": None,
            "level": 0,
            "lft": 1,
            "rght": 2,
            "tree_id": 0,
        }
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected_response, response.json())

    def test_publish_aggregate(self):
        baseurl = reverse(self.reverse_url)
        admin_url = baseurl + "1/publish_aggregate/"
        dev_url = baseurl + "2/publish_aggregate/"
        fed_url = reverse("model-list")
        version_data = {"version": "2.0.0"}

        # validate anonymous user cannot publish a model
        self._validate_unauthorized(dev_url, client_action=self.client.post)

        # validate client cannot publish an aggregate
        self.login_client(client_json={"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"})
        response = self.client.post(admin_url, data=version_data, format="json")
        self.assertEqual(403, response.status_code)
        expected_response = {
            "detail": "You do not have permission to perform this action."
        }
        self.assertDictEqual(expected_response, response.json())

        # validate developer can publish aggregate owned by them
        self.login_user(user_json={"username": "non_admin"})
        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open"
        ) as mock_load:
            # Turn aggregation results into file
            mock_load.return_value = utils.create_model_file([5, 2, 3])
            response = self.client.post(dev_url, data=version_data, format="json")
        self.assertEqual(201, response.status_code)
        expected_response = {
            "id": 1,
            "values": "/mediafiles/fake/path/model_aggregate/2",
            "version": "2.0.0",
            "created_on": response.json()["created_on"],
            "federated_model": 2,
        }
        self.assertDictEqual(expected_response, response.json())

        # Retrieve fed model for comparison of current artifact
        url = fed_url + "2/get_current_artifact/"
        fed_response = self.client.get(url, format="json")
        self.assertEqual(200, fed_response.status_code)
        model_art_from_fed = models.ModelArtifact.objects.filter(
            id=expected_response["id"],
            version=expected_response["version"],
        )
        self.assertEqual(1, model_art_from_fed.count())

        # Check if federated model is using new published aggregate
        self.assertDictEqual(expected_response, fed_response.json())

        fed_model = models.FederatedModel.objects.get(id=2)
        self.assertEqual(fed_model.current_artifact, model_art_from_fed.first())

        # validate developer cannot publish aggregate not owned by them
        self.login_user(user_json={"username": "non_admin"})
        response = self.client.post(admin_url, data=version_data, format="json")
        self.assertEqual(404, response.status_code)
        expected_response = {"detail": "Not found."}

        self.assertDictEqual(expected_response, response.json())

        # validate developer cannot publish a non-existent aggregate
        self.login_user(user_json={"username": "non_admin"})

        response = self.client.post(
            baseurl + "3/publish_aggregate/", data=version_data, format="json"
        )
        self.assertEqual(404, response.status_code)
        expected_response = {"detail": "Not found."}
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

    def test_pull_aggregate(self):
        baseurl = reverse(self.reverse_url)
        dev_url = baseurl + "2/"
        admin_url = baseurl + "1/"
        # validate anonymous user cannot publish a model
        self._validate_unauthorized(dev_url, client_action=self.client.get)

        # validate client cannot pull an aggregate
        self.login_client(client_json={"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"})
        response = self.client.get(dev_url, format="json")
        self.assertEqual(404, response.status_code)
        expected_response = {"detail": "Not found."}
        self.assertDictEqual(expected_response, response.json())

        # validate developer can pull aggregate owned by them
        self.login_user(user_json={"username": "non_admin"})

        with mock.patch(
            "django.core.files.storage.FileSystemStorage._open"
        ) as mock_load:
            mock_load.return_value = utils.create_model_file([5, 2, 3])
            response = self.client.get(dev_url, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {
            "id": 2,
            "result": [5, 2, 3],
            "validation_score": None,
            "created_on": "2023-01-20T23:08:28.712000Z",
            "lft": 1,
            "rght": 2,
            "tree_id": 1,
            "level": 0,
            "federated_model": 2,
            "parent": None,
        }
        self.assertDictEqual(expected_response, response.json())

        # validate developer cannot pull aggregate not owned by them
        response = self.client.get(admin_url, format="json")
        self.assertEqual(404, response.status_code)
        expected_response = {"detail": "Not found."}
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

    def test_update_val_score(self):
        baseurl = reverse(self.reverse_url)
        dev_url = baseurl + "2/"
        admin_url = baseurl + "1/"
        # validate anonymous user cannot publish a model
        self._validate_unauthorized(dev_url, client_action=self.client.patch)

        # validate client cannot pull an aggregate
        self.login_client(client_json={"uuid": "531580e6-ce6c-4f01-a5aa-9ed7af5ee768"})
        data = {"validation_score": 0.5}
        response = self.client.patch(dev_url, data=data, format="json")
        self.assertEqual(403, response.status_code)
        expected_response = {
            "detail": "You do not have permission to perform this action."
        }
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

        # validate developer can pull aggregate owned by them
        self.login_user(user_json={"username": "non_admin"})
        data = {"validation_score": 0.5}
        response = self.client.patch(dev_url, data=data, format="json")
        self.assertEqual(200, response.status_code)
        expected_response = {
            "id": 2,
            "result": "http://testserver/mediafiles/fake/path/model_aggregate/2",
            "validation_score": 0.5,
            "created_on": "2023-01-20T23:08:28.712000Z",
            "lft": 1,
            "rght": 2,
            "tree_id": 1,
            "level": 0,
            "federated_model": 2,
            "parent": None,
        }
        self.assertDictEqual(expected_response, response.json())

        # validate developer cannot pull aggregate not owned by them
        self.login_user(user_json={"username": "non_admin"})
        data = {"validation_score": 0.5}
        response = self.client.patch(admin_url, data=data, format="json")
        self.assertEqual(404, response.status_code)
        expected_response = {"detail": "Not found."}
        self.assertDictEqual(expected_response, response.json())
        self.logout_user()

    @mock.patch("rest_framework.mixins.ListModelMixin.list")
    def test_token_login(self, mock_list):
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
                "id": 1,
                "federated_model": 1,
                "result": "http://testserver/mediafiles/fake/path/model_aggregate/1",
                "validation_score": 1.0,
                "created_on": "2023-01-13T23:08:28.712000Z",
                "parent": None,
                "level": 0,
                "lft": 1,
                "rght": 2,
                "tree_id": 0,
            }
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

        # validate federated_model=2
        queryurl = baseurl + "?federated_model=2"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 2,
                "federated_model": 2,
                "result": "http://testserver/mediafiles/fake/path/model_aggregate/2",
                "validation_score": None,
                "created_on": "2023-01-20T23:08:28.712000Z",
                "parent": None,
                "level": 0,
                "lft": 1,
                "rght": 2,
                "tree_id": 1,
            },
        ]
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())

    def test_ordering(self, *mocks):
        baseurl = reverse(self.reverse_url)

        # validate validation_score
        queryurl = baseurl + "?ordering=validation_score"
        self.login_user(user_json={"username": "admin"})
        response = self.client.get(queryurl, format="json")
        expected_response = [
            {
                "id": 2,
                "federated_model": 2,
                "result": "http://testserver/mediafiles/fake/path/model_aggregate/2",
                "validation_score": None,
                "created_on": "2023-01-20T23:08:28.712000Z",
                "parent": None,
                "level": 0,
                "lft": 1,
                "rght": 2,
                "tree_id": 1,
            },
            {
                "id": 1,
                "federated_model": 1,
                "result": "http://testserver/mediafiles/fake/path/model_aggregate/1",
                "validation_score": 1.0,
                "created_on": "2023-01-13T23:08:28.712000Z",
                "parent": None,
                "level": 0,
                "lft": 1,
                "rght": 2,
                "tree_id": 0,
            },
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
