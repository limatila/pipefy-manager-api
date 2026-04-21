from sqlmodel import Field

from src.core.models import BaseModel


class Card(BaseModel, table=True):
	__tablename__ = "cards"

	pipe_card_id: str = Field(nullable=False, index=True, unique=True)
	current_phase_id: str | None = Field(default=None, index=True)
	is_final_phase: bool = Field(default=False, nullable=False)
