from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.dtos.lookup import PhaseSearchResponse
from src.middleware.auth import get_authenticated_person
from src.models.api_persons import ApiPerson
from src.services.phases_service import PhaseService

router = APIRouter(prefix="/phase", tags=["Phases"])


@router.get("", response_model=PhaseSearchResponse)
def search_phases(
    name: str | None = Query(default=None, description="Phase name to filter by (optional)"),
    person: ApiPerson = Depends(get_authenticated_person),
):
    service = PhaseService()
    try:
        return service.search_phases(name=name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
