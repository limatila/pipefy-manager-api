from datetime import datetime

from sqlmodel import Field, SQLModel

from core.config import PROJECT_TZ


class BaseModel(SQLModel, table=False):
    """
    Abstract base model shared by concrete SQLModel entities.
    """
    __abstract__ = True

    id: int | None = Field(default=None, primary_key=True)
    date_created: datetime = Field(
        default_factory=lambda: datetime.now(PROJECT_TZ),
        nullable=False,
    )
    date_updated: datetime = Field(
        default_factory=lambda: datetime.now(PROJECT_TZ),
        nullable=False,
    )
