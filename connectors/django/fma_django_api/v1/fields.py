"""Contains helper classes for serializing data into JSON format for file storage."""
import json

from rest_framework import serializers

from fma_django_api import utils


class JsonToInternalFileField(serializers.FileField):
    """Serializes model weights data into JSON."""

    def to_internal_value(self, data):
        """Converts data to a serialized set.

        :param data: the model weights
        :type data: Union[List, numpy.ndarray]
        :return: a set containing the serialized data
        :rtype: Set
        """
        data = utils.create_model_file(data)
        return super().to_internal_value(data)


class JsonFileField(serializers.FileField):
    """Reads a JSON file as a dictionary."""

    def to_representation(self, value):
        """Reads a JSON file as a dictionary.

        :param value: a file containing data about the model
        :type value: Any
        :return: a dictionary object containing the contents of the given file
        :rtype: Optional[Dict]
        """
        if value is None:
            return None
        with value.open("r") as f:
            return json.load(f)
