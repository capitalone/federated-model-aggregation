"""If errors, aws-xray-sdk patched this may be able to be removed.

This code is sliced from a future version of the aws-xray-sdk not yet merged.
https://github.com/aws/aws-xray-sdk-python/pull/350/files
"""

import wrapt
from aws_xray_sdk.ext.dbapi2 import XRayTracedConn, XRayTracedCursor


def patch():
    """Patches xray function wrapper."""
    wrapt.wrap_function_wrapper(
        "psycopg2.extras", "register_default_jsonb", _xray_register_default_jsonb_fix
    )


def _xray_register_default_jsonb_fix(wrapped, instance, args, kwargs):
    our_kwargs = dict()
    for key, value in kwargs.items():
        if key == "conn_or_curs" and isinstance(
            value, (XRayTracedConn, XRayTracedCursor)
        ):
            # unwrap the connection or cursor to be sent to register_default_jsonb
            value = value.__wrapped__
        our_kwargs[key] = value

    return wrapped(*args, **our_kwargs)
