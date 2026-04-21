from pydantic import BaseModel as PydanticBaseModel, Field


class ApiPersonCreateRequest(PydanticBaseModel):
    name: str = Field(min_length=3, max_length=50)


class ApiPersonCreateResponse(PydanticBaseModel):
    id: int
    name: str
    token: str
