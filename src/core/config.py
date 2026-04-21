from os import getenv
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv('.env')


PIPEFY_TOKEN = getenv("PIPEFY_TOKEN")
PIPE_ID = getenv("PIPE_ID", "303843596")

DB_URL = getenv("DB_URL", "sqlite:///./db.sqlite")
IS_CREATE_DEMO_API_STARTUP = getenv("CREATE_DEMO_API_STARTUP", "true").lower() == "true"

PROJECT_TIMEZONE = getenv("PROJECT_TIMEZONE", "America/Fortaleza")
PROJECT_TZ = ZoneInfo(PROJECT_TIMEZONE)

PIPEFY_GRAPHQL_ENDPOINT = "https://api.pipefy.com/graphql"
PIPEFY_GRAPHQL_TIMEOUT_SECONDS = float(
	getenv("PIPEFY_GRAPHQL_TIMEOUT_SECONDS", "30"),
)

API_BOOTSTRAP_PERSON_NAME = getenv("API_BOOTSTRAP_PERSON_NAME", "demo-api-person")

PIPEFY_FIELD_ID_NAME = getenv("PIPEFY_FIELD_ID_NAME", "name")
PIPEFY_FIELD_ID_EMAIL = getenv("PIPEFY_FIELD_ID_EMAIL", "email")
PIPEFY_FIELD_ID_TAX_ID = getenv("PIPEFY_FIELD_ID_TAX_ID", "tax_id")
