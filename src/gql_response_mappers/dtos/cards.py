# Dtos for graphql operations builder
from typing import Any, Optional

from pydantic import (
    BaseModel as PydanticBaseModel,
    Field
)

from src.core.config import (
    CIDADE_TABLE_ID, PIPE_ID
)


class GraphQLResult(PydanticBaseModel):
    data: Optional[dict[str, Any]] = None
    errors: list[dict[str, Any]] = Field(default_factory=list)


class CreateCardInput(PydanticBaseModel):
    pipe_id: str
    phase_id: Optional[str] = None
    fields_attributes: list[dict[str, Any]] = Field(default_factory=list)


class DeleteCardInput(PydanticBaseModel):
    card_id: str


class MoveCardToPhaseInput(PydanticBaseModel):
    card_id: str
    next_phase: Optional[bool] = False
    destination_phase_id: Optional[str] = None


class FetchPipePhasesInput(PydanticBaseModel):
    pipe_id: str = PIPE_ID


class FetchTableRecordsInput(PydanticBaseModel):
    table_id: str = CIDADE_TABLE_ID
