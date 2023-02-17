"""Set secret keys for api use."""
import os
import secrets

SECRET_KEY = str(os.environ.get("SECRET_KEY", None))
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(50)
