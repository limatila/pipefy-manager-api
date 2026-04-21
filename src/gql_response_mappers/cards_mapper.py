from src.core.config import (
    PIPE_ID,
)
from src.gql_response_mappers.dtos.cards import CreateCardInput
from src.dtos.cards import (
    CardCreateRequest,
    CardCreateResponse,
    CardDeleteResponse,
    CardMoveResponse,
)

PIPEFY_FIELD_ID_NAME = "name"
PIPEFY_FIELD_ID_EMAIL = "email"
PIPEFY_FIELD_ID_TAX_ID = "tax_id"


class CardsMapper:
    def __init__(self):
        self.pipe_id = PIPE_ID
        self.field_map = {
            "name": PIPEFY_FIELD_ID_NAME,
            "email": PIPEFY_FIELD_ID_EMAIL,
            "tax_id": PIPEFY_FIELD_ID_TAX_ID,
        }

    def to_create_card_input(self, payload: CardCreateRequest) -> CreateCardInput:
        raw_fields = {
            "name": payload.name,
            "email": payload.email,
            "tax_id": payload.tax_id,
        }

        fields_attributes: list[dict[str, str]] = []
        for source_key, target_field_id in self.field_map.items():
            value = raw_fields.get(source_key)
            if value is None:
                continue
            fields_attributes.append(
                {"field_id": target_field_id, "field_value": value}
            )

        return CreateCardInput(
            pipe_id=self.pipe_id,
            phase_id=payload.phase_id,
            fields_attributes=fields_attributes,
        )

    @staticmethod
    def from_create_card_data(card_data: dict) -> CardCreateResponse:
        current_phase = card_data.get("current_phase") or {}
        return CardCreateResponse(
            card_id=card_data["id"],
            current_phase_id=current_phase.get("id"),
            is_final_phase=False,
        )

    @staticmethod
    def to_delete_response(card_id: str, deleted: bool) -> CardDeleteResponse:
        return CardDeleteResponse(card_id=card_id, deleted=deleted)

    @staticmethod
    def to_move_response(
        *,
        card_id: str,
        previous_phase_id: str | None,
        current_phase_id: str | None,
        moved: bool,
        is_final_phase: bool,
    ) -> CardMoveResponse:
        return CardMoveResponse(
            card_id=card_id,
            previous_phase_id=previous_phase_id,
            current_phase_id=current_phase_id,
            moved=moved,
            is_final_phase=is_final_phase,
        )
