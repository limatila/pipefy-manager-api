from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import SQLModel, Session, create_engine

from .models import *
from .config import DB_URL

from src.services.person_service import ApiPersonService


class DatabaseManager:
    def __init__(self, db_url: str):
        self.engine = create_engine(
            db_url,
            echo=False,
            connect_args=self._connect_args(db_url),
        )

    @staticmethod
    def _connect_args(db_url: str) -> dict[str, bool]:
        if db_url.startswith("sqlite"):
            return {"check_same_thread": False}
        return {}

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def create_demo_api_person(self):
        with database_manager.session_context() as session:
            person, created = ApiPersonService.bootstrap_demo_person(session)
            if created:
                print(
                    "[startup] Demo ApiPerson created "
                    f"\t**name='{person.name}' token='{person.token}'"
                )

    @contextmanager
    def session_context(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            try:
                yield session
            finally:
                session.close()


database_manager = DatabaseManager(DB_URL)


def get_db_session() -> Generator[Session, None, None]:
    with database_manager.session_context() as session:
        yield session
