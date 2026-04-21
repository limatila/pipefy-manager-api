from pydantic import BaseModel as PydanticBaseModel, Field


class CardCreateRequest(PydanticBaseModel):
    name: str = Field(min_length=3, max_length=120)
    cpf: str = Field(default=None, max_length=32)
    cidade: str = Field(default=None, max_length=50)
    phase_id: str | None = Field(default=None, min_length=1)


class CardCreateResponse(PydanticBaseModel):
    card_id: str
    current_phase_id: str | None = None
    is_final_phase: bool = False


class CardDeleteResponse(PydanticBaseModel):
    card_id: str
    deleted: bool


class CardMoveRequest(PydanticBaseModel):
    destination_phase_id: str = Field(min_length=1)


class CardMoveResponse(PydanticBaseModel):
    card_id: str
    previous_phase_id: str | None = None
    current_phase_id: str | None = None
    moved: bool
    is_final_phase: bool