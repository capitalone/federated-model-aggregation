"""API Service Handlers for FMA Django."""
import logging

import django
from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from fma_core.workflows.api_handler_utils import register as register_api_handler

try:
    from apig_wsgi import make_lambda_handler
except ModuleNotFoundError as e:
    # apig_wsgi is only needed for the api_handler
    if "No module named 'apig_wsgi'" not in str(e):
        raise

if not apps.ready and not settings.configured:
    django.setup()


logger = logging.getLogger()
logger.setLevel(logging.INFO)


_real_handler = None


@register_api_handler()
def django_lambda_handler(event, context):
    """Entry point for web requests."""
    global _real_handler
    if _real_handler is None:
        application = get_wsgi_application()
        _real_handler = make_lambda_handler(application, binary_support=True)
    try:
        handler_ret_val = _real_handler(event, context)
    except Exception as e:
        logger.error(e)
        raise
    logger.warning(f"_real_handler return value {handler_ret_val}")
    logger.warning(f"_real_handler type {type(handler_ret_val)}")
    return handler_ret_val
