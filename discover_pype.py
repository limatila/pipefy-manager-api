# discover_pipe.py  — run once, read-only, delete after use
import json
from src.core.config import PIPEFY_TOKEN, PIPE_ID, PIPEFY_GRAPHQL_ENDPOINT
from src.pipefy_clients.pipefy_graphql_client import PipefyGraphQLClient, PipefyResponseParser

client = PipefyGraphQLClient(endpoint=PIPEFY_GRAPHQL_ENDPOINT, token=PIPEFY_TOKEN)
parser = PipefyResponseParser()

# --- query 1: all fields (start form + each phase) ---
fields_query = """
query DiscoverFields($pipeId: ID!) {
  pipe(id: $pipeId) {
    id
    name
    start_form_fields {
      id
      label
      type
      required
    }
    phases {
      id
      name
      fields {
        id
        label
        type
        required
      }
    }
  }
}
"""

# --- query 2: phases in order ---
phases_query = """
query FetchPipePhases($pipeId: ID!) {
  pipe(id: $pipeId) {
    phases {
      id
      name
    }
  }
}
"""

# --- query 3: introspect PhaseField to find connector-source fields ---
introspect_phase_field_query = """
{
  __type(name: "PhaseField") {
    fields { name }
  }
}
"""

# --- query 4: table records ---
table_records_query = """
query FetchTableRecords($tableId: ID!) {
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

print("=" * 60)
print(f"PIPE_ID resolved to: {PIPE_ID!r}")
print("=" * 60)

r1 = parser.normalize(client.execute(fields_query, {"pipeId": PIPE_ID}))
print("\n[FIELDS DISCOVERY]")
print(json.dumps(r1, indent=2, ensure_ascii=False))

r2 = parser.normalize(client.execute(phases_query, {"pipeId": PIPE_ID}))
print("\n[PHASES DISCOVERY]")
print(json.dumps(r2, indent=2, ensure_ascii=False))

# Introspect PhaseField to find the connector-source field name
r3 = parser.normalize(client.execute(introspect_phase_field_query, {}))
all_field_names = [f["name"] for f in (((r3.get("data") or {}).get("__type") or {}).get("fields") or [])]
connector_related = [n for n in all_field_names if any(k in n.lower() for k in ("connect", "repo", "table", "source", "child", "parent"))]
print(f"\n[PhaseField connector-related field names]: {connector_related}")
print(f"[All PhaseField names]: {all_field_names}")

# Introspect PublicRepoUnion to get correct type names
repo_union_query = """
{
  __type(name: "PublicRepoUnion") {
    possibleTypes { name }
  }
}
"""
rpu = parser.normalize(client.execute(repo_union_query, {}))
possible_types = [t["name"] for t in (((rpu.get("data") or {}).get("__type") or {}).get("possibleTypes") or [])]
print(f"\n[PublicRepoUnion possible types]: {possible_types}")

# Build fragment string dynamically from possible types
fragments = "\n".join(f"        ... on {t} {{ id name __typename }}" for t in possible_types) or "        id"
connected_repo_query = f"""
query ConnectedRepo($pipeId: ID!) {{
  pipe(id: $pipeId) {{
    start_form_fields {{
      id
      label
      type
      connectedRepo {{
{fragments}
      }}
    }}
  }}
}}
"""
rcr = parser.normalize(client.execute(connected_repo_query, {"pipeId": PIPE_ID}))
print("\n[CONNECTED REPO PER FIELD]")
print(json.dumps(rcr, indent=2, ensure_ascii=False))

# Fetch records from the connected repo of cidade
start_fields = ((rcr.get("data") or {}).get("pipe") or {}).get("start_form_fields") or []
for f in start_fields:
    repo = f.get("connectedRepo")
    if not repo:
        continue
    repo_id = repo.get("id")
    repo_type = repo.get("__typename")
    repo_name = repo.get("name")
    print(f"\n[FIELD '{f['id']}' connects to {repo_type} '{repo_name}' id={repo_id}]")
    if repo_type == "Table":
        r4 = parser.normalize(client.execute(table_records_query, {"tableId": repo_id}))
    else:
        r4 = parser.normalize(client.execute("""
            query($id: ID!) { pipe(id: $id) { cards(first: 50) { edges { node { id title } } } } }
        """, {"id": repo_id}))
    print(json.dumps(r4, indent=2, ensure_ascii=False))