"""Configuration for the fma-core library."""
import copy
import importlib
import os


class Settings:
    """Settings Module for the fma-core library."""

    def __init__(self):
        """Imports user specified settings file from env."""
        settings_module = os.environ.get("FMA_SETTINGS_MODULE", None)
        if not settings_module:
            raise ImportError("The `FMA_SETTINGS_MODULE` was not set.")
        mod = importlib.import_module(settings_module)
        agg_settings = getattr(mod, "AGGREGATOR_SETTINGS", None)
        if not agg_settings or not isinstance(agg_settings, dict):
            raise ValueError(
                "`FMA_SETTINGS_MODULE` is imporpery configured and must "
                "contain the dict `AGGREGATOR_SETTINGS`"
            )
        for attr in dir(mod):
            value = getattr(mod, attr)
            # avoids issues if modules imported
            if isinstance(value, (list, dict)):
                value = copy.deepcopy(value)
            setattr(self, attr, value)


settings = Settings()
