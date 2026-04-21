from sqlmodel import Field

from src.core.models import BaseModel


class Person(BaseModel, table=True):
    __tablename__ = "persons"

    name: str = Field(nullable=False)
    email: str = Field(nullable=False, index=True)
    token_hash: str = Field(nullable=False, index=True, unique=True)