---
name: graphql-abstraction
description: 'Build minimal and scalable Pipefy GraphQL integration around 3 initial endpoints (create, delete, move phase with final-phase response), using simple dynamic operation string generation, Bearer-token client, and normalized parser for data/errors.'
argument-hint: 'Which operation flow are you adding: create, delete, move phase, or fetch phases?'
---

# GraphQL Abstraction

## Outcome
- Build reusable GraphQL components for Pipefy with minimal ceremony.
- Keep operation building, transport, and response parsing strictly separated.
- Start from 3 essential operations and scale to new operations with consistent interfaces.
- Return a predictable normalized shape: `{data, errors}`.

## When to Use
- You are implementing or refactoring Pipefy integration for:
    - create card from Pessoa data
    - delete card by ID
    - move card phase and support final-phase detection response
- You want dynamic but simple string-based GraphQL operation generation.
- You need to keep growth path open for new endpoints without rewriting architecture.

## Design Constraints
- Prefer raw string query construction over generated SDKs.
- Keep methods pure where possible.
- Use only lightweight HTTP libraries (`requests` default or `httpx` when async is needed).
- Keep operation builder hyper simple and dynamic, avoiding hardcoded duplication.
- Avoid overengineering and unnecessary class hierarchies.
- Keep service-facing integration methods as focused defs that execute mapped operations.
- Allow small standalone pure helpers only when they reduce duplication.
- Keep naming and signatures uniform across builder, client, and parser.

## Required Components
- `PipefyOperationBuilder`: builds GraphQL strings and variables only.
- `PipefyGraphQLClient`: executes HTTP calls only (Bearer auth, endpoint, timeout).
- `PipefyResponseParser`: normalizes provider responses only.
- Pydantic DTOs for operation payload validation (request/response boundaries live outside client).

## Core Operations First
1. `createCard`
- Uses mapped Pessoa fields.
- Returns normalized card payload for downstream mapper/DTO conversion.

2. `deleteCard`
- Uses card ID only.
- Returns success status normalized from GraphQL response.

3. `moveCardToPhase`
- Uses card ID + destination phase ID.
- Returns moved card phase data for final-phase evaluation in service layer.

4. `fetchPipePhases` (supporting helper)
- Used to determine final phase when needed by move flow.

## Procedure
1. Define Pydantic models for each operation input.
2. Implement dynamic builder primitives to compose operation strings and variables.
3. Expose operation-specific methods that call those primitives and return `(query, variables)`.
4. Implement one client class that sends GraphQL payloads and returns raw JSON.
5. Implement one parser class that always returns `{data, errors}`.
6. Keep business rules (including final-phase interpretation) in service layer, not in builder/client/parser.
7. Reuse common class interfaces as operations grow.
8. Add tests for validation, dynamic query generation, and response normalization.

## Decision Points
- Use `requests` for synchronous code paths.
- Prefer GraphQL variables over direct string interpolation for values.
- If `errors` exists in the response, always surface it in normalized output, even when `data` exists.
- If operation shape repeats (mutation name, vars, selection set), extract a small dynamic builder helper instead of copy/paste.
- If new endpoint is similar to existing operation, add new operation method before adding new classes.

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
    def _build_operation(
        operation_type: str,
        operation_name: str,
        variable_declaration: str,
        operation_body: str,
    ) -> str:
        return f"""
        {operation_type} {operation_name}{variable_declaration} {{
          {operation_body}
        }}
        """

    @staticmethod
    def create_card(payload: CreateCardInput) -> str:
        ...

    @staticmethod
    def delete_card(payload: DeleteCardInput) -> str:
        ...

    @staticmethod
    def move_card_to_phase(payload: MoveCardInput) -> str:
        ...

    @staticmethod
    def fetch_pipe_phases(payload: FetchPipePhasesInput) -> str:
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
    def delete_card(payload: DeleteCardInput) -> str:
        query = f"""
        mutation DeleteCard($cardId: ID!) {
          deleteCard(input: {{ id: $cardId }}) {{
            success
          }}
        }
        """
        return query


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
- Builder supports dynamic operation composition with simple reusable primitives.
- Core integration flow remains class-based and simple, without over-abstraction.
- Bearer auth is always sent as `Authorization: Bearer <token>`.
- Unit tests cover at least one success and one error response.
- Move flow has coverage for final-phase signaling behavior (service-level).
