from secrets import token_urlsafe

from sqlmodel import Session, select

from src.core.config import API_BOOTSTRAP_PERSON_NAME
from src.models.persons import ApiPerson


class ApiPersonService:
    @staticmethod
    def bootstrap_demo_person(session: Session) -> tuple[ApiPerson, bool]:
        existing = session.exec(select(ApiPerson)).first()
        if existing is not None:
            return existing, False

        token = token_urlsafe(32)
        
        person = ApiPerson(name=API_BOOTSTRAP_PERSON_NAME, cpf='000.000.000-12', token=token)
        
        session.add(person)
        session.commit()
        session.refresh(person)
        
        return person, True
