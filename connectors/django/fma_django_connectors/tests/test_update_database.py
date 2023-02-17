import pytest
from django.conf import settings
from django.db import connection
from django.test import TransactionTestCase
from pytest_django import fixtures

from fma_django_connectors.metadata_connector import DjangoMetadataConnector
from fma_django_connectors.tests import fma_settings


@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"]["TEST"]["MIGRATE"] = False
    settings.DATABASES["default"]["NAME"] = ":memory:"


class TestUpdateDatabase(TransactionTestCase):
    def test_update(self):
        # resets connection clearing the db for sqlite...
        connection.connect()
        table_names = connection.introspection.table_names()
        assert len(table_names) == 0

        # calls function to apply migration
        agg_settings = fma_settings.AGGREGATOR_SETTINGS
        DjangoMetadataConnector(settings=agg_settings).update_database()

        # check to see if migrations applied
        table_names = connection.introspection.table_names()
        assert len(table_names) > 0
