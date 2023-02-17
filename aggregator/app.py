"""Application main file, this is where the lambda functionality is written."""
import json
import logging
from dataclasses import dataclass

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.api_gateway import ALBResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from fma_core.workflows.tasks import agg_service, post_agg_service_hook

import patch_xray

# Can be removed when xray is updated and the patch is live.
patch_xray.patch()

URL_PREFIX = ""

logger = Logger()
logger.setLevel(logging.INFO)
tracer = Tracer()


# A aws_lambda_powertools application is used to route the ALB event to various
# endpoints.  The @app markup below maps the functions to various endpoints and
# HTTP methods
app = ALBResolver()


# TODO: abstract to fma-core
@dataclass
class Task:
    """Used to construct a valid parameter for the post_agg_service function."""

    args: list
    success: bool

    def __init__(self, args, success):
        """Initialization of the Task class.

        :param args: Arguments
        :type args: Dict, optional
        :param success: The initial task success status
        :type success: bool
        """
        self.args = args
        self.success = success


@app.get("/health")
@tracer.capture_method
def health_check():
    """A health check endpoint needed to register an API with a gateway.

    :return: An ALB response.
    :rtype: aws_lambda_powertools.event_handler.api_gateway.Response
    """
    response_body = {"status": "healthy"}
    return Response(
        status_code=200, body=json.dumps(response_body), content_type="application/json"
    )


@app.get(f"{URL_PREFIX}/example")
@app.get(f"{URL_PREFIX}/example/")
@tracer.capture_method
def example_get():
    """An example API endpoint that could be registered with a gateway.

    Change this endpoint and the associated path to be specific to the API
    being implemented


    :return: An ALB response.
    :rtype: aws_lambda_powertools.event_handler.api_gateway.Response
    """
    response_body = {"data": {"message": "Hello World"}}
    #
    # Response must be in the format that the ALB understands
    return Response(
        status_code=200, body=json.dumps(response_body), content_type="application/json"
    )


def validate_federated_model_id_as_int(id):
    """Sanitizes the federated model id as an integer.

    Casts the federated model id to an integer.
    Raises ValueError if 'id' is not castable to an integer.

    :param id: The id of the Federated Model
    :type id: int, float, str
    :raises ValueError: the federated_model_id could not be converted to an int
    :return: the federated model id as an integer
    :rtype: int
    """
    try:
        id: int = int(id)
    except ValueError:
        raise ValueError("the federated_model_id could not be converted to an int")
    return id


def create_response(response_body, status_code=200):
    """Creates valid lambda response with body inserted.

    :param response_body: The response body returned
    :type response_body: Union[str, int, float, bool, None, List, Dict]
    :param status_code: The status code of the response,
        defaults to 200
    :type status_code: int, optional
    :return: The full response with the statusCode, headers, and body
    :rtype: Dict[('statusCode': <status_code>),
        ('headers': { 'Content-type' : 'application/json' }),
        ('body': <response_body>)]
    """
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
    """Utilizes the ALBResolver to route the event to the appropriate function.

    :param event: Metadata about the event
    :type event: Dict
    :param context: The body of the event
    :type context: Any
    :return: The response from the event
    :rtype: Dict
    """
    logger.info(context)
    logger.info(event)

    if "httpMethod" not in event:
        fed_id = event.get("detail", {}).get("model_id", None)
        if not fed_id:
            return create_response({"data": "NO MODEL ID PROVIDED"}, status_code=400)
        fed_id = validate_federated_model_id_as_int(fed_id)

        # default to False
        success = False
        agg_id = None
        try:
            agg_id = agg_service(fed_id)
            success = True
        except Exception as e:
            logger.error(e)
        finally:
            task = Task(args=[fed_id], success=success)
            post_agg_service_hook(task)
        if agg_id:
            logger.info("AGGREGATE CREATED: {}".format(agg_id))
        return create_response({"data": dict(fed_id=fed_id, agg_id=agg_id)})

    return app.resolve(event, context)
