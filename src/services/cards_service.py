from sqlmodel import Session, select

from src.core.service import BaseService
from src.gql_response_mappers.dtos.cards import DeleteCardInput, FetchPipePhasesInput, MoveCardToPhaseInput
from src.dtos.cards import (
    CardCreateRequest,
    CardCreateResponse,
    CardDeleteResponse,
    CardMoveRequest,
    CardMoveResponse,
)
from src.gql_response_mappers.cards_mapper import CardsMapper
from src.models.cards import Card
from src.models.api_persons import ApiPerson


class CardsService(BaseService):
    def __init__(self, mapper: CardsMapper | None = None):
        self.mapper = mapper or CardsMapper()

    def create_card(
        self,
        session: Session,
        person: ApiPerson,
        payload: CardCreateRequest,
    ) -> CardCreateResponse:
        builder = self._builder_cls()
        client = self._client()
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
        client = self._client()

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
        client = self._client()

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

        phases_query, phases_variables = builder.fetch_pipe_phases(
            FetchPipePhasesInput()
        )
        phases_result = self._normalize_response(client.execute(phases_query, phases_variables))
        phases = ((phases_result.get("data") or {}).get("pipe") or {}).get("phases") or []
        final_phase_id = phases[-1]["id"] if phases else None
        is_final_phase = bool(current_phase_id and final_phase_id and current_phase_id == final_phase_id)

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
