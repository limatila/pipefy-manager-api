from os import getenv
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv('.env')


#* PIPEFY
PIPEFY_TOKEN = getenv("PIPEFY_TOKEN")
PIPE_ID = getenv("PIPE_ID")

PIPEFY_GRAPHQL_ENDPOINT = "https://api.pipefy.com/graphql"
PIPEFY_GRAPHQL_TIMEOUT_SECONDS = float(
	getenv("PIPEFY_GRAPHQL_TIMEOUT_SECONDS", "30"),
)


#* SQLModel
DB_URL = getenv("DB_URL", "sqlite:///./db.sqlite")

PROJECT_TIMEZONE = getenv("PROJECT_TIMEZONE", "America/Fortaleza")
PROJECT_TZ = ZoneInfo(PROJECT_TIMEZONE)


#* DEMO
IS_CREATE_DEMO_API_STARTUP = getenv("CREATE_DEMO_API_STARTUP", "true").lower() == "true"
API_BOOTSTRAP_PERSON_NAME = getenv("API_BOOTSTRAP_PERSON_NAME", "demo-api-person")

