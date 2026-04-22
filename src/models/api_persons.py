from sqlmodel import Field

from src.core.models import BaseModel


class ApiPerson(BaseModel, table=True):
    __tablename__ = "persons"

    name: str = Field(nullable=False)
    token: str = Field(nullable=False, index=True, unique=True)