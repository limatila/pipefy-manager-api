from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from src.core.database import get_db_session
from src.models.persons import ApiPerson

bearer_scheme = HTTPBearer(auto_error=False)


def get_authenticated_person(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_db_session),
) -> ApiPerson:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    person = session.exec(
        select(ApiPerson).where(ApiPerson.token == credentials.credentials)
    ).first()
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, not found token",
        )

    return person
