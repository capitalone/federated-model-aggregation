"""API Exception class."""


class APIException(Exception):
    """Base class for REST framework exceptions.

    Subclasses should provide `.status_code` and `.default_detail` properties.
    """

    def __init__(self, status_code=None, message=None):
        """
        Initialize APIException.

        :param status_code: status_code
        :type status_code: int
        :param message: API Code message
        :type message: str
        """
        if message is None:
            message = "Could not connect to the server."
        if status_code is None:
            status_code = "NULL"
        self.error_message = ("An API error occurred (status_code={}): {}").format(
            status_code, str(message)
        )

    def __str__(self):
        """Format API error message as a string."""
        return str(self.error_message)
