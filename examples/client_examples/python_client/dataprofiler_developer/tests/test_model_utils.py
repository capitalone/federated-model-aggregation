import os
import sys
import unittest

TEST_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
CLIENT_ROOT_DIR = os.path.dirname(TEST_ROOT_DIR)
sys.path.append(CLIENT_ROOT_DIR)
import model_utils  # noqa: E402


class TestModelUtils(unittest.TestCase):
    def test_weight_extraction(self):
        weights = model_utils.extract_data_profiler_weights()
        self.assertIsNot(weights, None)
        self.assertIsInstance(weights, list)
