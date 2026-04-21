---
name: graphql-abstraction
description: 'Build minimal and robust Python GraphQL integrations for Pipefy. Use for class-based query and mutation builders, Bearer-token clients (requests default, httpx optional), Pydantic validation, normalized data/errors parsing, and reusable helpers for createCard, deleteCard, moveCardToPhase, and pipe phases.'
argument-hint: 'What operation do you need: createCard, deleteCard, moveCardToPhase, or fetch phases?'
---

# GraphQL Abstraction

## Outcome
- Build small reusable class-based components for GraphQL calls against a single endpoint.
- Keep responsibilities separated into operation builder, execution client, and response parser.
- Validate inputs with Pydantic and return a predictable normalized shape: `{data, errors}`.

## When to Use
- You need to add or refactor Pipefy GraphQL integrations.
- You want string-based queries and mutations without heavy GraphQL frameworks.
- You need reusable helpers for createCard, deleteCard, moveCardToPhase, or fetching phases.

## Design Constraints
- Prefer raw string query construction over generated SDKs.
- Keep methods pure where possible.
- Use only lightweight HTTP libraries (`requests` default or `httpx` when async is needed).
- Keep code simple enough to implement quickly, but structured to scale with new operations.
- Avoid overengineering and avoid unnecessary class hierarchies.
- Avoid arbitrary and scattered standalone `def` blocks for integration behavior.
- Allow small standalone pure helpers only when they are reusable and reduce duplication.
- Keep naming and method signatures uniform across builder, client, and parser, without forcing rigid ceremony.

## Required Components
- `PipefyOperationBuilder`: builds GraphQL strings and variables only.
- `PipefyGraphQLClient`: executes HTTP calls only (Bearer auth, endpoint, timeout).
- `PipefyResponseParser`: normalizes provider responses only.
- Pydantic input models for operation payloads and validation.

## Procedure
1. Define Pydantic models for each operation input.
2. Implement builder methods returning `(query, variables)` for each operation.
3. Implement one client class that sends GraphQL payloads and returns raw JSON.
4. Implement one parser class that returns only `{data, errors}`.
5. Keep business rules in service layer, not in builder or client.
6. Reuse common class interfaces to keep the module uniform as operations grow.
7. Add tests for validation, query generation, and response normalization.

## Decision Points
- Use `requests` for synchronous code paths.
- Use `httpx` only when async support is required.
- Prefer GraphQL variables over direct string interpolation for values.
- If `errors` exists in the response, always surface it in normalized output, even when `data` exists.

## Suggested Class Shapes
```python
from typing import Any
from pydantic import BaseModel, Field

class CreateCardInput(BaseModel):
    pipe_id: str
    phase_id: str
    fields: dict[str, Any] = Field(default_factory=dict)

class DeleteCardInput(BaseModel):
    card_id: str

class MoveCardInput(BaseModel):
    card_id: str
    destination_phase_id: str

class FetchPipePhasesInput(BaseModel):
    pipe_id: str


class PipefyOperationBuilder:
    @staticmethod
    def create_card(payload: CreateCardInput) -> tuple[str, dict[str, Any]]:
        ...

    @staticmethod
    def delete_card(payload: DeleteCardInput) -> tuple[str, dict[str, Any]]:
        ...

    @staticmethod
    def move_card_to_phase(payload: MoveCardInput) -> tuple[str, dict[str, Any]]:
        ...

    @staticmethod
    def fetch_pipe_phases(payload: FetchPipePhasesInput) -> tuple[str, dict[str, Any]]:
        ...


class PipefyGraphQLClient:
    def __init__(self, endpoint: str, token: str, timeout: float = 30.0):
        ...

    def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        ...


class PipefyResponseParser:
    @staticmethod
    def normalize(payload: dict[str, Any]) -> dict[str, Any]:
        """Return {'data': Any, 'errors': list[dict]} with stable keys."""
        ...
```

## Minimal Patterns
```python
class PipefyOperationBuilder:
    @staticmethod
    def delete_card(payload: DeleteCardInput) -> tuple[str, dict[str, str]]:
        query = """
        mutation DeleteCard($cardId: ID!) {
          deleteCard(input: { id: $cardId }) {
            success
          }
        }
        """
        return query, {"cardId": payload.card_id}


class PipefyResponseParser:
    @staticmethod
    def normalize(payload: dict) -> dict:
        return {
            "data": payload.get("data"),
            "errors": payload.get("errors", []),
        }
```

## Completion Checklist
- Query builders do not perform network calls.
- Execution client does not know operation-specific business rules.
- Pydantic models validate payloads before query generation.
- Parser always returns the same normalized shape: `{data, errors}`.
- Builder methods exist for createCard, deleteCard, moveCardToPhase, and fetch phases.
- Core integration flow is class-based, without arbitrary free-function sprawl.
- Implementation remains uniform and readable, but not rigid or over-abstracted.
- Bearer auth is always sent as `Authorization: Bearer <token>`.
- Unit tests cover at least one success and one error response.
