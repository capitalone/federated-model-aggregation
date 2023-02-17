from __future__ import annotations

import os
import sys
import unittest
from dataclasses import dataclass
from unittest import mock

import numpy as np

from fma_core.algorithms.aggregators.common import average_layers, avg_values_if_data
from fma_core.tests import utils


class TestAvgValues(unittest.TestCase):
    def test_no_model_updates(self, *mocks):
        model = None
        model_updates = []
        actual_result = avg_values_if_data(model, model_updates)
        self.assertTrue(np.isnan(actual_result))

    def test_multilayer_array(self, *mocks):
        model = None
        model_updates = [
            utils.ModelUpdate(data=[[2], [2]], client=utils.Client("id=1")),
            utils.ModelUpdate(data=[[3], [1]], client=utils.Client("id=2")),
        ]
        expected_result = [[2.5], [1.5]]
        actual_result = average_layers(model, model_updates)
        self.assertListEqual(expected_result, actual_result)


class TestAvgLayers(unittest.TestCase):
    def test_no_model_updates(self, *mocks):
        model = None
        model_updates = []
        actual_result = average_layers(model, model_updates)
        self.assertIsNone(actual_result)

    def test_multilayer_array(self, *mocks):
        model = None
        model_updates = [
            utils.ModelUpdate(data=[[2], [2, 4, 5], [2]], client=utils.Client("id=1")),
            utils.ModelUpdate(data=[[3], [1, 3, 4], [1]], client=utils.Client("id=2")),
        ]
        expected_result = [[2.5], [1.5, 3.5, 4.5], [1.5]]
        actual_result = average_layers(model, model_updates)
        self.assertListEqual(expected_result, actual_result)
