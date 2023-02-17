import unittest
from unittest import mock

from fma_core.workflows.aggregator_connectors_factory import BaseAggConnector
from fma_core.workflows.aggregator_utils import AutoSubRegistrationMeta


class TestBaseAggreagtorFactory(unittest.TestCase):
    @mock.patch(
        "fma_core.workflows.aggregator_connectors_factory.BaseAggConnector."
        "_BaseAggConnector__subclasses",
        new_callable=mock.PropertyMock,
    )
    def test_auto_register_subclass(self, mock_subclasses, *mocks):

        # create fake class
        class FakeAggConn(BaseAggConnector, metaclass=AutoSubRegistrationMeta):
            def __init__(self, settings=None):
                pass

        # assert registered
        BaseAggConnector._BaseAggConnector__subclasses.__setitem__.assert_called_with(
            "fakeaggconn", FakeAggConn
        )

        # assert can get after register
        mock_subclasses.return_value = {"fakeaggconn": FakeAggConn}
        value = BaseAggConnector.create("fakeaggconn")
        self.assertIsInstance(value, FakeAggConn)
