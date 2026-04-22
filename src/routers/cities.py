from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.dtos.lookup import CitySearchResponse
from src.middleware.auth import get_authenticated_person
from src.models.api_persons import ApiPerson
from src.services.cities_service import CityService

router = APIRouter(prefix="/city", tags=["Cities"])


@router.get("", response_model=CitySearchResponse)
def search_cities(
    name: str = Query(..., min_length=1, description="City name to search for"),
    person: ApiPerson = Depends(get_authenticated_person),
):
    service = CityService()
    try:
        return service.search_cities(name=name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
