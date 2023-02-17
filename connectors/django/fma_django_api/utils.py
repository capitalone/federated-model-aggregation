"""Contains utility functions for handling data sent to the FMA Django API."""
import json
import uuid
from io import BytesIO

from django.core.files.uploadedfile import UploadedFile


def create_model_file(data):
    """Create a django json file object of the model weights data.

    :param data: Model weights data
    :type data: Any
    :return: a json object of the model weights and metadata expected by the API service
    :rtype: django.core.files.uploadedfile.UploadedFile
    """
    data_io = BytesIO(json.dumps(data).encode("utf-8"))
    data = UploadedFile(data_io)
    data.name = str(uuid.uuid4())
    data.size = data_io.getbuffer().nbytes
    return data
