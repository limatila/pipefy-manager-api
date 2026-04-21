from secrets import token_urlsafe

from sqlmodel import Session, select

from src.core.config import API_BOOTSTRAP_PERSON_NAME
from src.dtos.persons import ApiPersonCreateRequest, ApiPersonCreateResponse
from src.models.persons import ApiPerson


class ApiPersonService:
    @staticmethod
    def create_person(
        session: Session,
        payload: ApiPersonCreateRequest,
    ) -> ApiPersonCreateResponse:
        existing = session.exec(
            select(ApiPerson).where(ApiPerson.name == payload.name)
        ).first()
        if existing is not None:
            raise ValueError("Name already exists")

        person = ApiPerson(name=payload.name, token=token_urlsafe(32))
        session.add(person)
        session.commit()
        session.refresh(person)

        return ApiPersonCreateResponse(id=person.id, name=person.name, token=person.token)

    @staticmethod
    def bootstrap_demo_person(session: Session) -> tuple[ApiPerson, bool]:
        existing = session.exec(select(ApiPerson)).first()
        if existing is not None:
            return existing, False

        token = token_urlsafe(32)
        
        person = ApiPerson(name=API_BOOTSTRAP_PERSON_NAME, token=token)
        
        session.add(person)
        session.commit()
        session.refresh(person)
        
        return person, True
