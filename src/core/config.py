from os import getenv
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv('.env')


PIPEFY_TOKEN = getenv("PIPEFY_TOKEN")
PIPE_ID = getenv("PIPE_ID")

DB_URL = getenv("DB_URL") or getenv("db.sqlite") or "sqlite:///./db.sqlite"

PROJECT_TIMEZONE = getenv("PROJECT_TIMEZONE", "America/Fortaleza")
PROJECT_TZ = ZoneInfo(PROJECT_TIMEZONE)

PIPEFY_GRAPHQL_ENDPOINT = "https://api.pipefy.com/graphql"
PIPEFY_GRAPHQL_TIMEOUT_SECONDS = float(
	getenv("PIPEFY_GRAPHQL_TIMEOUT_SECONDS", "30"),
)
