import unittest
from unittest.mock import patch

from sqlmodel import Session, SQLModel, create_engine, select

from src.dtos.cards import CardCreateRequest, CardMoveRequest
from src.models.cards import Card
from src.models.api_persons import ApiPerson
from src.services.cards_service import CardsService


class _FakeParser:
    @staticmethod
    def normalize(payload):
        return payload


class _FakeBuilder:
    @staticmethod
    def create_card(payload):
        return "create", {"pipeId": payload.pipe_id}

    @staticmethod
    def delete_card(payload):
        return "delete", {"cardId": payload.card_id}

    @staticmethod
    def move_card_to_phase(payload):
        return "move", {"cardId": payload.card_id}

    @staticmethod
    def fetch_pipe_phases(payload):
        return "phases", {"pipeId": payload.pipe_id}


class _FakeClient:
    def __init__(self, endpoint, token, timeout):
        self.endpoint = endpoint
        self.token = token
        self.timeout = timeout

    def execute(self, query, variables):
        if query == "create":
            return {
                "data": {
                    "createCard": {
                        "card": {
                            "id": "card-1",
                            "current_phase": {"id": "phase-1", "name": "Fase 1"},
                        }
                    }
                },
                "errors": [],
            }

        if query == "delete":
            return {"data": {"deleteCard": {"success": True}}, "errors": []}

        if query == "move":
            return {
                "data": {
                    "moveCardToPhase": {
                        "card": {
                            "id": variables["cardId"],
                            "current_phase": {"id": "phase-2", "name": "Fase 2"},
                        }
                    }
                },
                "errors": [],
            }

        if query == "phases":
            return {
                "data": {
                    "pipe": {
                        "phases": [
                            {"id": "phase-1", "name": "Fase 1"},
                            {"id": "phase-2", "name": "Fase 2"},
                            {"id": "phase-final", "name": "Fase Final"},
                        ]
                    }
                },
                "errors": [],
            }

        return {"data": None, "errors": [{"message": "unexpected query"}]}


class CardsServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(self.engine)
        self.service = CardsService()

    def _components(self):
        return (_FakeClient, _FakeParser, _FakeBuilder)

    def test_create_card_persists_local_record(self):
        with Session(self.engine) as session:
            person = ApiPerson(name="demo", token="sec_token")
            session.add(person)
            session.commit()
            session.refresh(person)

            payload = CardCreateRequest(
                name="Alice",
                cpf="123",
                phase_id="phase-1",
            )
            with patch("src.core.service.get_pipefy_runtime_components", self._components):
                response = self.service.create_card(session=session, person=person, payload=payload)

            self.assertEqual("card-1", response.card_id)
            card = session.exec(select(Card).where(Card.pipe_card_id == "card-1")).first()
            self.assertIsNotNone(card)
            self.assertEqual("phase-1", card.current_phase_id)

    def test_delete_card_removes_local_record(self):
        with Session(self.engine) as session:
            person = ApiPerson(name="demo", token="sec_token")
            card = Card(pipe_card_id="card-1", current_phase_id="phase-1", is_final_phase=False)
            session.add(person)
            session.add(card)
            session.commit()
            session.refresh(person)

            with patch("src.core.service.get_pipefy_runtime_components", self._components):
                response = self.service.delete_card(session=session, person=person, card_id="card-1")

            self.assertTrue(response.deleted)
            still_exists = session.exec(select(Card).where(Card.pipe_card_id == "card-1")).first()
            self.assertIsNone(still_exists)

    def test_move_card_updates_phase_and_keeps_is_final_false(self):
        with Session(self.engine) as session:
            person = ApiPerson(name="demo", token="sec_token")
            card = Card(pipe_card_id="card-1", current_phase_id="phase-1", is_final_phase=False)
            session.add(person)
            session.add(card)
            session.commit()
            session.refresh(person)

            with patch("src.core.service.get_pipefy_runtime_components", self._components):
                response = self.service.move_card_to_phase(
                    session=session,
                    person=person,
                    card_id="card-1",
                    payload=CardMoveRequest(destination_phase_id="phase-2"),
                )

            self.assertTrue(response.moved)
            self.assertFalse(response.is_final_phase)
            updated = session.exec(select(Card).where(Card.pipe_card_id == "card-1")).first()
            self.assertIsNotNone(updated)
            self.assertEqual("phase-2", updated.current_phase_id)


if __name__ == "__main__":
    unittest.main()
