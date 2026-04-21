---
name: api-payload-architecture
description: 'Design scalable API boundaries for Pipefy integration centered on 3 core endpoints (create card from pessoa data, delete by card ID, move card phase with final-phase signal). Use for Pydantic DTO contracts, Router-Service-Mapper separation, local runtime persistence, and future endpoint expansion without overengineering.'
argument-hint: 'Which core endpoint are you implementing or extending: create, delete, or move phase?'
---

# API Payload Architecture

## Outcome
- Expose clean internal contracts while hiding Pipefy-specific payload details.
- Start from 3 essential endpoints and scale to new operations without breaking patterns.
- Keep translation rules centralized, deterministic, and testable.
- Preserve strict boundaries between Router, Service, Mapper, and GraphQL integration.

## When to Use
- You are implementing the foundational Pipefy endpoints:
    - create card from Pessoa registration fields
    - delete card by ID
    - move card phase and return final-phase state when reached
- You need DTO-first API contracts using internal language.
- You need to keep room for additional endpoints with minimal refactor.

## Layer Responsibilities
- Router: validates request DTOs, invokes service methods, returns response DTOs.
- Service: orchestrates mapping, GraphQL execution, response interpretation, and local persistence during runtime.
- Mapper: translates internal DTOs to provider payload and provider data to internal response DTOs.

## Core Endpoint Contracts
1. Create card endpoint
- Input DTO mirrors Pessoa domain fields.
- Service maps Pessoa fields to Pipefy fields, creates the card, and returns normalized internal response.

2. Delete card endpoint
- Input DTO contains card ID.
- Service calls deletion flow and returns success/error normalized response.

3. Move card endpoint
- Input DTO contains card ID and destination phase.
- Service moves card, then determines if card reached final phase.
- Response must include final-phase flag (for example `is_final_phase: bool`).

## Required Architecture Pattern
- Use a configurable mapper class, not scattered standalone mapper defs.
- Use Pydantic models for public request and response DTOs.
- Keep GraphQL query or mutation creation separate from payload mapping.
- Keep GraphQL transport separate from both mapper and service logic.
- Keep service methods as focused defs that execute mapped operations (avoid unnecessary class layering).
- Keep implementation intentionally simple: do not overbuild for early scope.
- Allow standalone pure helper defs only when clearly reusable and not orchestration-critical.

## Procedure
1. Define request/response DTOs (Pydantic) for create, delete, and move endpoints.
2. Define mapping dictionaries from internal Pessoa/domain fields to Pipefy field IDs.
3. Implement mapper methods for:
     - request DTO -> Pipefy variables payload
     - Pipefy response -> internal response DTO
4. Keep router minimal: validate DTO, call service, return DTO.
5. In service, execute flow: map -> build GraphQL operation -> call client -> parse -> persist local runtime data -> return DTO.
6. For move endpoint, compare destination/current phase with final phase reference and set final-phase flag in response.
7. Keep naming and method signatures uniform so adding new endpoints follows same recipe.
8. Add tests for DTO validation, mapper output determinism, and phase-finalization behavior.

## Decision Points
- If Pipefy field IDs change, update only mapper dictionaries.
- If business rule is workflow-specific (for example final phase semantics), keep it in service.
- If a provider field has no internal equivalent, handle it in mapper defaults, never in public DTO.
- If runtime persistence grows beyond lightweight needs, preserve service contract and swap storage implementation.
- If new endpoints are added, reuse DTO + mapper + service composition before introducing new abstractions.

## Suggested Mapper Pattern
```python
from typing import Any
from pydantic import BaseModel, Field

class CreatePersonCardRequest(BaseModel):
    title: str
    description: str | None = None
    tax_id: str
    phase_name: str | None = None


class PersonCardResponse(BaseModel):
    id: str
    title: str
    fields: dict[str, Any] = Field(default_factory=dict)


class PipefyPayloadMapper:
    def __init__(self, field_map: dict[str, str]):
        self.field_map = field_map

    def to_pipefy_fields(self, dto: CreatePersonCardRequest) -> list[dict[str, Any]]:
        payload = dto.model_dump(exclude_none=True)
        translated: list[dict[str, Any]] = []
        for internal_key, external_key in self.field_map.items():
            if internal_key in payload:
                translated.append(
                    {"field_id": external_key, "field_value": payload[internal_key]}
                )
        return translated


    def from_pipefy_card(self, card: dict[str, Any]) -> PersonCardResponse:
        return PersonCardResponse(
            id=card["id"],
            title=card.get("title", ""),
            fields={item["name"]: item.get("value") for item in card.get("fields", [])},
        )
```

## Service Composition Pattern
- Router receives HTTP payload and validates with Pydantic DTO.
- Service calls mapper to produce external input fields.
- Service calls GraphQL builder to produce `(query, variables)`.
- Service calls GraphQL client to execute the request.
- Service calls parser and mapper to produce public response DTO.
- Service persists relevant runtime state in local DB.
- Router returns DTO response without provider internals.

## Completion Checklist
- Public DTOs do not expose `field_id`, `phase_id`, or external GraphQL-specific internals.
- Router does not contain mapping logic.
- Mapper does not contain HTTP concerns.
- Service does not leak raw provider payloads to API responses.
- Mapper is class-based, configurable by field map, and reusable across use cases.
- Public DTOs are validated with Pydantic before integration calls.
- Field translation is centralized in mapping dictionaries.
- Service persists runtime-relevant data in local DB where required by flow.
- Move endpoint response includes final-phase information.
- Core orchestration remains simple and avoids unnecessary abstractions.
- Code style is uniform and readable without excessive rigidity.
- Mapper tests validate both directions where applicable.

## Integration Note
- Pair this skill with `graphql-abstraction` to keep translation, operation building, transport, and parsing fully separated.
