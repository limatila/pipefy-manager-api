import json
from src.core.config import PIPEFY_TOKEN, PIPEFY_GRAPHQL_ENDPOINT, CIDADE_TABLE_ID
from src.pipefy_clients.pipefy_graphql_client import PipefyGraphQLClient, PipefyResponseParser

client = PipefyGraphQLClient(endpoint=PIPEFY_GRAPHQL_ENDPOINT, token=PIPEFY_TOKEN)
parser = PipefyResponseParser()

query = """
query FetchCidades($tableId: ID!) {
  table_records(table_id: $tableId, first: 50) {
    edges {
      node {
        id
        title
      }
    }
  }
}
"""

r = parser.normalize(client.execute(query, {"tableId": CIDADE_TABLE_ID}))

# Extract simplified list
records = (((r.get("data") or {}).get("table_records") or {}).get("edges") or [])
cidades = [{"id": e["node"]["id"], "name": e["node"]["title"]} for e in records if e.get("node")]
print(json.dumps({"errors": r.get("errors"), "data": cidades}, indent=2, ensure_ascii=False))
