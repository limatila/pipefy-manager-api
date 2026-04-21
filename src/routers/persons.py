from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.middleware.auth import get_authenticated_person
from src.core.database import get_db_session
from src.dtos.persons import ApiPersonCreateRequest, ApiPersonCreateResponse
from src.models.persons import ApiPerson
from src.services.person_service import ApiPersonService

router = APIRouter(prefix="/api-persons", tags=["Api Person"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiPersonCreateResponse,
)
def create_api_person(
    payload: ApiPersonCreateRequest,
    _: ApiPerson = Depends(get_authenticated_person),
    session: Session = Depends(get_db_session),
):
    try:
        return ApiPersonService.create_person(session=session, payload=payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc