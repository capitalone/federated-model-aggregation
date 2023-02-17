"""Registry and registration functions related to the api handler factory."""
from typing import Callable

_registry = {}


def register() -> Callable:
    """Decorator for registering a function as an api_handler."""

    def wrapper(fcn: Callable):
        """Wrapper inside the decorator for adding to the registry."""
        fcn_name = fcn.__name__
        if fcn_name not in _registry:
            _registry[fcn_name] = fcn
        return fcn

    return wrapper
