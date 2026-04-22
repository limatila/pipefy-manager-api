from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.middleware.auth import get_authenticated_person
from src.core.database import get_db_session
from src.dtos.cards import (
    CardCreateRequest,
    CardCreateResponse,
    CardDeleteResponse,
    CardMoveRequest,
    CardMoveResponse,
)
from src.models.api_persons import ApiPerson
from src.services.cards_service import CardsService

router = APIRouter(prefix="/card", tags=["Card Management"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CardCreateResponse,
)
def create_card(
    payload: CardCreateRequest,
    person: ApiPerson = Depends(get_authenticated_person),
    session: Session = Depends(get_db_session),
):
    service = CardsService()
    try:
        return service.create_card(session=session, person=person, payload=payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete("/{card_id}", response_model=CardDeleteResponse)
def delete_card(
    card_id: str,
    person: ApiPerson = Depends(get_authenticated_person),
    session: Session = Depends(get_db_session),
):
    service = CardsService()
    try:
        return service.delete_card(session=session, person=person, card_id=card_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch("/{card_id}/move", response_model=CardMoveResponse)
def move_card_to_phase(
    card_id: str,
    payload: CardMoveRequest,
    person: ApiPerson = Depends(get_authenticated_person),
    session: Session = Depends(get_db_session),
):
    service = CardsService()
    try:
        return service.move_card_to_phase(
            session=session,
            person=person,
            card_id=card_id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
