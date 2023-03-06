from .version import __version__


def setup():
    """Loads packages required for the fma-core listed in the settings."""
    import importlib

    from fma_core.conf import settings

    packages = getattr(settings, "INSTALLED_PACKAGES", [])
    for package in packages:
        importlib.import_module(package)
