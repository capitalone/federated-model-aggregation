"""File for initialization of the service."""
import json
import logging

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from fma_core.workflows import api_handler_factory
from fma_core.workflows.tasks import update_metadata_db

import patch_xray

# Can be removed when xray is updated and the patch is live.
patch_xray.patch()

logging.basicConfig()
logger = Logger()
logger.setLevel(logging.INFO)
tracer = Tracer()


def create_response(response_body, status_code=200):
    """Creates valid lambda response with body inserted."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(response_body),
    }


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.APPLICATION_LOAD_BALANCER
)
@tracer.capture_lambda_handler
def handler(event, context):
    """Handler for service initialization."""
    if "update_metadata_db" in event.get("detail", {}):
        update_metadata_db()
        data = {"data": "database updated successfully"}
        return create_response(data)

    logger.warning(f"context return value {context}")
    logger.warning(f"context type {type(context)}")
    logger.warning(f"event return value {event}")
    logger.warning(f"event type {type(event)}")
    return api_handler_factory.call_api_handler(event, context)
