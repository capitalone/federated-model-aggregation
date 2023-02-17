"""Web Client file."""

import os
from typing import Any

import requests

from fma_connect import exceptions, settings


class WebClient:
    """REST API Wrapper to interact with the federated learning service."""

    def __init__(self, federated_model_id, uuid=None, url=None):
        """Initialization function for WebClient.

        :param federated_model_id: id of the federated model for which to send
            updates
        :type federated_model_id: int
        :param uuid: client uuid, None if not previously registered
        :type uuid: str
        :param url: url of the api, by default uses settings
        :type url: str
        """
        if url is None:
            url = settings.default_url
        self._url = url
        self._uuid = uuid
        self._federated_model_id = federated_model_id
        self._is_registered = False
        self._last_model_aggregate = None

    @property
    def uuid(self):
        """Client uuid."""
        if self._uuid is None:
            self._uuid = self.register()
        return self._uuid

    @property
    def url(self):
        """URL of the API."""
        return self._url

    @property
    def federated_model_id(self):
        """ID of the federated model for which to send updates."""
        return self._federated_model_id

    def _get_auth_header(self, uuid=None):
        """Generates the request auth header for the client.

        :param uuid: client uuid, None if not previously registered
        :type uuid: int
        :return: dict of headers for the request
        :rtype: Dict[('CLIENT-UUID': str)]
        """
        if uuid is None:
            uuid = self._uuid
        return {"CLIENT-UUID": uuid}

    def register(self):
        """Registers client with federated model.

        Registers the client with the federated model. If the client is already
        registered, no changes will be made.

        :raises APIException: response is something other than 200 or 201
        :return: string of the registered uuid
        :rtype: str
        """
        auth_header = None
        if self._uuid:
            auth_header = self._get_auth_header()
        url = os.path.join(
            self.url, "api/v1/models", str(self._federated_model_id), "register_client/"
        )

        response = requests.post(url, headers=auth_header, timeout=10)
        if response.status_code not in [200, 201]:
            raise exceptions.APIException(
                status_code=response.status_code, message=response.json()
            )
        self._uuid = response.json()["uuid"]
        self._is_registered = True
        return response.json()["uuid"]

    def send_update(self, data: Any, base_aggregate=None) -> dict:
        """
        Sends updates to the API service.

        :param data: the updates to the weights you intend of sending to API
        :type data: Any
        :param base_aggregate: the starting aggregate which your updates are based on,
            defaults to None
        :type base_aggregate: Any, optional
        :raises APIException: response status code is something other than 201
        :return: a dictionary of the response from the FMA Service
            :model_data: The stored weights that now exist within the service's database
        :rtype: Dict[('model_data': Any)]
        """
        auth_header = None
        if self._uuid:
            auth_header = self._get_auth_header()

        params = {
            "federated_model": self._federated_model_id,
            "data": data,
            "base_aggregate": base_aggregate,
        }
        url = os.path.join(self.url, "api/v1/model_updates/")
        response = requests.post(url, headers=auth_header, json=params, timeout=10)
        if response.status_code != 201:
            raise exceptions.APIException(
                status_code=response.status_code, message=response.json()
            )
        return response.json()

    def check_for_new_model_aggregate(self, update_after=None):
        """
        Retrieves the latest model aggregate for the model.

        :param update_after: aggregate id that any new aggregate has to be more
            than, defaults to None
        :type update_after: int, optional
        :raises APIException: response status code is something other than 200
        :return: response of the api in json format
            :id: model aggregate object identifier
            :results: output of the aggregation function (ie updated model weights)
            :validation_score: output of the specified evaluation function
        :rtype: Optional[Dict[('id': int),
            ('results': Any),
            ('validation_score': float)]]
        """
        auth_header = None
        if self._uuid:
            auth_header = self._get_auth_header()

        url = os.path.join(
            self.url,
            "api/v1/models",
            str(self._federated_model_id),
            "get_latest_aggregate/",
        )
        response = requests.get(url, headers=auth_header, timeout=10)
        if response.status_code != 200:
            raise exceptions.APIException(
                status_code=response.status_code, message=response.json()
            )

        model_agg = response.json()
        if not model_agg:
            return None
        response_agg_id = model_agg["id"]

        # if latest agg is not new, don't return the aggregate
        last_model_aggregate = update_after or self._last_model_aggregate
        if last_model_aggregate is not None and last_model_aggregate >= response_agg_id:
            model_agg = None

        # update to latest

        if update_after:
            response_agg_id = max(response_agg_id, self._last_model_aggregate)
        self._last_model_aggregate = response_agg_id
        return model_agg

    def get_current_artifact(self):
        """
        Retrieves the latest artifact for the model.

        :raises APIException: response status code is something other than 200
        :return: response of the API in json format
            :id: id of the artifact object
            :values: model weights of the published artifact
            :version: version of the model artifact published to production
                inference environment
            :created_on: timestamp
            :federated_model: id of the base federated model object}
        :rtype: Optional[Dict[('id': int),
            ('values': Any),
            ('created_on': str),
            ('federated_model': int)]]
        """
        auth_header = None
        if self._uuid:
            auth_header = self._get_auth_header()

        url = os.path.join(
            self.url,
            "api/v1/models",
            str(self._federated_model_id),
            "get_current_artifact/",
        )
        response = requests.get(url, headers=auth_header, timeout=10)
        if response.status_code != 200:
            raise exceptions.APIException(
                status_code=response.status_code, message=response.json()
            )
        return response.json()

    def check_for_latest_model(self, update_after=None):
        """Retrieves latest update to Federated Model.

        Retrieves latest update to Federated model based on timestamp
        regardless of artifact or aggregate.

        :param update_after: aggregate id that any new aggregate has to be more
            than, defaults to None
        :type update_after: int, optional
        :raises APIException: response status code is something other than 200
        :return: response of the api in json format
            :values: The data to be loaded into model schema
            :aggregate: the id of the aggregate the values were pulled from
                (None if pulling from artifact)
        :rtype: Optional[Dict[('values': Any), ('aggregate': int)]]
        """
        auth_header = None
        if self._uuid:
            auth_header = self._get_auth_header()

        url = os.path.join(
            self.url,
            "api/v1/models",
            str(self._federated_model_id),
            "get_latest_model/",
        )
        response = requests.get(url, headers=auth_header, timeout=10)
        if response.status_code != 200:
            raise exceptions.APIException(
                status_code=response.status_code, message=response.json()
            )
        model_agg = response.json()
        if not model_agg:
            return None
        response_agg_id = (
            model_agg["aggregate"] if model_agg["aggregate"] is not None else -1
        )

        # if latest agg is not new, don't return the aggregate
        last_model_aggregate = update_after or self._last_model_aggregate
        if last_model_aggregate is not None and last_model_aggregate >= response_agg_id:
            model_agg = None
        # update to latest
        if update_after:
            response_agg_id = max(response_agg_id, self._last_model_aggregate)
        self._last_model_aggregate = response_agg_id
        return model_agg

    def send_val_results(self, results: Any, aggregate_id: int) -> dict:
        """
        Sends updates to the FMA service.

        :param results: the updates to the weights you intend of sending to FMA
        :type results: Any
        :param aggregate_id: the starting aggregate your updates are based on
        :type aggregate_id: int
        :raises APIException: response status code is something other than 201
        :return: a dictionary of the response from the FMA Service in json format
            :results: a copy of the pushed results including the status of the API call
        :rtype: Dict
        """
        auth_header = None
        if self._uuid:
            auth_header = self._get_auth_header()

        params = {
            "validation_results": results,
            "federated_model": self._federated_model_id,
            "aggregate": aggregate_id,
            "client": self._uuid,
        }
        url = os.path.join(self.url, "api/v1/client_aggregate_scores/")
        response = requests.post(url, headers=auth_header, json=params, timeout=10)
        if response.status_code != 201:
            raise exceptions.APIException(
                status_code=response.status_code, message=response.json()
            )

        return response.json()
