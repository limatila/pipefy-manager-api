from sqlmodel import Field

from src.core.models import BaseModel


class Assignee(BaseModel, table=True):
    __tablename__ = "assignees"

    pipe_user_id: str = Field(nullable=False, index=True)
    name: str = Field(nullable=False)