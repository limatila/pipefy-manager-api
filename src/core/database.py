from collections.abc import Generator

from sqlmodel import SQLModel, Session, create_engine

from core.config import DB_URL


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

    def create_tables(self) -> None:
        # Import models before create_all so metadata includes all tables.
        from models.api_users
        import models.assignees
        import models.cards
        import models.persons

        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            yield session


database_manager = DatabaseManager(DB_URL)