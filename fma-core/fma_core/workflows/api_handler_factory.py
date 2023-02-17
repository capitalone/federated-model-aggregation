"""Factory function for calling registered api handlers specified in settings."""
from typing import Any

from fma_core.conf import settings as fma_settings
from fma_core.workflows.api_handler_utils import _registry


def call_api_handler(*args, **kwargs) -> Any:
    """Abstract call to API handler of a connector."""
    handler_settings = getattr(fma_settings, "API_SERVICE_SETTINGS", None)
    if not handler_settings:
        raise ValueError(
            "`API_SERVICE_SETTINGS` settings are not specified in settings"
        )
    handler_fcn_str = handler_settings.get("handler", None)
    if handler_fcn_str is None:
        raise ValueError("`handler` is not specified in settings")

    handler_fcn = _registry[handler_fcn_str]
    return handler_fcn(*args, **kwargs)
