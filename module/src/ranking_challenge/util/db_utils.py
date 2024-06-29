import logging
import os
import json

from sqlalchemy.engine.url import URL
from urllib.parse import urlparse, parse_qs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S,%f",
)

logger = logging.getLogger(__name__)


def build_db_uri(source_uri=None):
    """This is a helper function to inject postgres credentials from env vars
    into a connection string.

    Args:
        source_uri (Optional[str]): base connection string, if not provided, will
            use the DB_URI environment variable

    It is needed because the URI components may be passed in the DB_URI environment
    variable in their entirety (e.g. in local testing), but in production, the secrets
    secrets are generally passed in as separate environment variables.

    This function implements the following logic:
    - if PGPASSWORD is set, use it as the password and PGUSER (default: postgres)
      as the username
    - if POSTGRES_CREDENTIALS is set, assume it contains a JSON object of the form
          {"username": "myuser", "password": "mypass"}
    - if none of the above conditions apply, return DB_URI as given
    """
    if source_uri is None:
        source_uri = os.getenv("DB_URI")
    if source_uri is None:
        logger.error("DB_URI not set and source_uri not provided")
        raise Exception("DB_URI not set and source_uri not provided")
    parsed_uri = urlparse(source_uri)
    if parsed_uri.scheme == "":
        logger.error("Invalid URI scheme")
        raise Exception("Invalid URI scheme")
    query = {}
    if parsed_uri.query:
        query = parse_qs(parsed_uri.query)
    username = parsed_uri.username or "postgres"
    password = ""
    if os.getenv("PGPASSWORD"):
        password = os.getenv("PGPASSWORD")
    if os.getenv("PGUSER"):
        username = os.getenv("PGUSER")
    if not (username and password):
        if (env_creds := os.getenv("POSTGRES_CREDENTIALS")) is not None:
            creds = json.loads(env_creds)
            username = creds.get("username", username)
            password = creds.get("password", password)
    if not (username and password):
        return source_uri
    return URL(
        drivername=parsed_uri.scheme,
        username=username,
        password=password,
        host=parsed_uri.hostname,
        port=parsed_uri.port,
        database=parsed_uri.path.lstrip("/"),
        query=query,  # type:ignore
    )
