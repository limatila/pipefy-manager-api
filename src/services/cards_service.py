from sqlmodel import Session, select

from src.core.config import (
    PIPEFY_GRAPHQL_ENDPOINT,
    PIPEFY_GRAPHQL_TIMEOUT_SECONDS,
)
from src.gql_response_mappers.dtos.cards import DeleteCardInput, MoveCardToPhaseInput
from src.dtos.cards import (
    CardCreateRequest,
    CardCreateResponse,
    CardDeleteResponse,
    CardMoveRequest,
    CardMoveResponse,
)
from src.gql_response_mappers.cards_mapper import CardsMapper
from src.models.cards import Card
from src.models.persons import ApiPerson
from src.middleware.pipefy_runtime import get_pipefy_runtime_components


class CardsService:
    def __init__(self, mapper: CardsMapper | None = None):
        self.mapper = mapper or CardsMapper()

    @staticmethod
    def _normalize_response(payload: dict) -> dict:
        _, parser_cls, _ = get_pipefy_runtime_components()
        return parser_cls.normalize(payload)

    @staticmethod
    def _builder_cls():
        _, _, builder_cls = get_pipefy_runtime_components()
        return builder_cls

    @staticmethod
    def _client_for_person(person: ApiPerson):
        client_cls, _, _ = get_pipefy_runtime_components()
        return client_cls(
            endpoint=PIPEFY_GRAPHQL_ENDPOINT,
            token=person.token,
            timeout=PIPEFY_GRAPHQL_TIMEOUT_SECONDS,
        )

    @staticmethod
    def _raise_if_pipefy_errors(normalized: dict):
        errors = normalized.get("errors", [])
        if errors:
            first_error = errors[0] if isinstance(errors[0], dict) else {"message": str(errors[0])}
            raise ValueError(first_error.get("message", "Pipefy error"))

    def create_card(
        self,
        session: Session,
        person: ApiPerson,
        payload: CardCreateRequest,
    ) -> CardCreateResponse:
        builder = self._builder_cls()
        client = self._client_for_person(person)
        create_input = self.mapper.to_create_card_input(payload)

        query, variables = builder.create_card(create_input)
        normalized = self._normalize_response(client.execute(query, variables))
        self._raise_if_pipefy_errors(normalized)

        card_data = (((normalized.get("data") or {}).get("createCard") or {}).get("card"))
        if not card_data:
            raise ValueError("Pipefy did not return card data")

        current_phase = card_data.get("current_phase") or {}
        record = session.exec(
            select(Card).where(Card.pipe_card_id == card_data["id"])
        ).first()
        if record is None:
            record = Card(pipe_card_id=card_data["id"])

        record.current_phase_id = current_phase.get("id")
        record.is_final_phase = False
        session.add(record)
        session.commit()

        return self.mapper.from_create_card_data(card_data)

    def delete_card(
        self,
        session: Session,
        person: ApiPerson,
        card_id: str,
    ) -> CardDeleteResponse:
        builder = self._builder_cls()
        client = self._client_for_person(person)

        query, variables = builder.delete_card(DeleteCardInput(card_id=card_id))
        normalized = self._normalize_response(client.execute(query, variables))
        self._raise_if_pipefy_errors(normalized)

        deleted = bool((((normalized.get("data") or {}).get("deleteCard") or {}).get("success")))

        if deleted:
            record = session.exec(select(Card).where(Card.pipe_card_id == card_id)).first()
            if record is not None:
                session.delete(record)
                session.commit()

        return self.mapper.to_delete_response(card_id=card_id, deleted=deleted)

    def move_card_to_phase(
        self,
        session: Session,
        person: ApiPerson,
        card_id: str,
        payload: CardMoveRequest,
    ) -> CardMoveResponse:
        builder = self._builder_cls()
        client = self._client_for_person(person)

        previous_record = session.exec(
            select(Card).where(Card.pipe_card_id == card_id)
        ).first()
        previous_phase_id = previous_record.current_phase_id if previous_record else None

        move_input = MoveCardToPhaseInput(
            card_id=card_id,
            destination_phase_id=payload.destination_phase_id,
        )
        query, variables = builder.move_card_to_phase(move_input)
        normalized = self._normalize_response(client.execute(query, variables))
        self._raise_if_pipefy_errors(normalized)

        moved_card = (((normalized.get("data") or {}).get("moveCardToPhase") or {}).get("card"))
        moved = moved_card is not None
        current_phase = moved_card.get("current_phase") if moved_card else {}
        current_phase_id = current_phase.get("id") if isinstance(current_phase, dict) else None

        # Dynamic final-phase detection is intentionally deferred until builder supports fetch_pipe_phases.
        is_final_phase = False

        if moved:
            if previous_record is None:
                previous_record = Card(pipe_card_id=card_id)
            previous_record.current_phase_id = current_phase_id
            previous_record.is_final_phase = is_final_phase
            session.add(previous_record)
            session.commit()

        return self.mapper.to_move_response(
            card_id=card_id,
            previous_phase_id=previous_phase_id,
            current_phase_id=current_phase_id,
            moved=moved,
            is_final_phase=is_final_phase,
        )
