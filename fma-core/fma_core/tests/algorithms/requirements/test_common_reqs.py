from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

import numpy as np

from fma_core.algorithms.requirements.common import all_clients, require_x_updates
from fma_core.tests import utils


class TestAllClients(unittest.TestCase):
    def test_no_model_updates(self):
        model = utils.FederatedModel(clients=utils.ClientList([utils.Client("test")]))
        model_updates = []
        actual_result = all_clients(model, model_updates)
        self.assertFalse(actual_result)

    def test_fail_req(self):
        model = utils.FederatedModel(
            clients=utils.ClientList(
                [
                    utils.Client("id=1"),
                    utils.Client("id=2"),
                ]
            )
        )
        model_updates = [utils.ModelUpdate(client=utils.Client("id=2"), data=None)]
        actual_result = all_clients(model, model_updates)
        self.assertFalse(actual_result)

    def test_pass_req(self):
        model = utils.FederatedModel(
            clients=utils.ClientList(
                [
                    utils.Client("id=1"),
                    utils.Client("id=2"),
                ]
            )
        )
        model_updates = [
            utils.ModelUpdate(client=utils.Client("id=1"), data=None),
            utils.ModelUpdate(client=utils.Client("id=2"), data=None),
        ]
        actual_result = all_clients(model, model_updates)
        self.assertTrue(actual_result)


class TestRequireXUpdates(unittest.TestCase):
    def test_no_model_updates(self):
        model = utils.FederatedModel(clients=utils.ClientList([utils.Client("test")]))
        model_updates = []
        actual_result = require_x_updates(model, model_updates, x=3)
        self.assertFalse(actual_result)

    def test_fail_req(self):
        model = utils.FederatedModel(
            clients=utils.ClientList(
                [
                    utils.Client("id=1"),
                    utils.Client("id=2"),
                ]
            )
        )
        model_updates = [utils.ModelUpdate(client=utils.Client("id=2"), data=None)]
        actual_result = require_x_updates(model, model_updates, x=2)
        self.assertFalse(actual_result)

    def test_pass_req(self):
        model = utils.FederatedModel(
            clients=utils.ClientList(
                [
                    utils.Client("id=1"),
                    utils.Client("id=2"),
                    utils.Client("id=3"),
                ]
            )
        )
        # meet by having == 2
        model_updates = [
            utils.ModelUpdate(client=utils.Client("id=1"), data=None),
            utils.ModelUpdate(client=utils.Client("id=2"), data=None),
        ]
        actual_result = require_x_updates(model, model_updates, x=2)
        self.assertTrue(actual_result)

        # meet by having >= 2
        model_updates = [
            utils.ModelUpdate(client=utils.Client("id=1"), data=None),
            utils.ModelUpdate(client=utils.Client("id=2"), data=None),
            utils.ModelUpdate(client=utils.Client("id=3"), data=None),
        ]
        actual_result = require_x_updates(model, model_updates, x=2)
        self.assertTrue(actual_result)
