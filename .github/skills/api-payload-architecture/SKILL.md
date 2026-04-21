---
name: api-payload-architecture
description: 'Design clean API boundaries for Pipefy-style integrations with complex payloads. Use for Pydantic DTOs, class-based mapper architecture, internal-to-external translation, and strict Router-Service-Mapper separation without leaking external IDs in public contracts.'
argument-hint: 'Which endpoint or use case needs internal DTO to Pipefy payload translation?'
---

# API Payload Architecture

## Outcome
- Expose clean internal API contracts while hiding Pipefy payload complexity.
- Keep mapping rules centralized and testable.
- Preserve strict boundaries between HTTP, business logic, GraphQL building, and translation layers.

## When to Use
- Pipefy field structure is complex or non-intuitive for API consumers.
- You are creating or refactoring endpoints that should not expose external IDs.
- You need consistent payload translation for create, update, or move operations.

## Layer Responsibilities
- Router layer validates HTTP input and returns HTTP responses.
- Service layer orchestrates business rules and integration calls.
- Mapper layer translates between internal DTOs and Pipefy GraphQL payloads.

## Required Architecture Pattern
- Use a configurable mapper class, not scattered standalone mapper defs.
- Use Pydantic models for public request and response DTOs.
- Keep GraphQL query or mutation creation separate from payload mapping.
- Keep GraphQL transport separate from both mapper and service logic.
- Keep implementation simple enough for fast delivery, but scalable for new entities and operations.
- Keep patterns uniform across modules without forcing strict boilerplate everywhere.
- Allow standalone pure helper defs only when clearly reusable and not part of the core orchestration flow.

## Procedure
1. Define public DTOs as Pydantic models using internal domain language.
2. Create a mapper class initialized with field map dictionaries.
3. Add mapper methods for each translation direction and operation type.
4. Build GraphQL operations in a dedicated builder class.
5. Execute GraphQL requests in a dedicated client class.
6. Keep service methods as orchestrators of validation, mapping, builder, client, and parser.
7. Return only internal DTOs from service and router.
8. Keep interfaces and naming consistent to maintain uniform code as modules evolve.
9. Add tests for DTO validation, mapper determinism, and boundary compliance.

## Decision Points
- If external schema changes often, isolate all changes in mapper dictionaries.
- If transformation has business rules, keep validation in service and formatting in mapper.
- If state persistence is unnecessary, prefer stateless request-through mapping.
- If an external field has no internal equivalent, handle it with mapper defaults, not public DTO leakage.

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
- Router returns DTO response without provider internals.

## Completion Checklist
- Public DTOs do not expose `field_id`, `phase_id`, or external GraphQL-specific internals.
- Router does not contain mapping logic.
- Mapper does not contain HTTP concerns.
- Service does not leak raw provider payloads to API responses.
- Mapper is class-based, configurable by field map, and reusable across use cases.
- Public DTOs are validated with Pydantic before integration calls.
- Field translation is centralized in mapping dictionaries.
- Core orchestration avoids arbitrary standalone defs.
- Code style is uniform and readable without excessive rigidity.
- Mapper tests validate both directions where applicable.

## Integration Note
- Pair this skill with `graphql-abstraction` to keep translation, operation building, transport, and parsing fully separated.
