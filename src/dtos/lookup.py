from pydantic import BaseModel as PydanticBaseModel


class CityResult(PydanticBaseModel):
    id: str
    name: str


class CitySearchResponse(PydanticBaseModel):
    results: list[CityResult]


class PhaseResult(PydanticBaseModel):
    id: str
    name: str


class PhaseSearchResponse(PydanticBaseModel):
    results: list[PhaseResult]
