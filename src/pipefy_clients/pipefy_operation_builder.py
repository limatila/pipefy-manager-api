from typing import Any

from src.gql_response_mappers.dtos.cards import (
    CreateCardInput,
    DeleteCardInput,
    FetchPipePhasesInput,
    MoveCardToPhaseInput,
)


class PipefyOperationBuilder:
    @staticmethod
    def create_card(payload: CreateCardInput) -> tuple[str, dict[str, Any]]:
        query = """
        mutation CreateCard($pipeId: ID!, $phaseId: ID!, $fieldsAttributes: [FieldValueInput!]!) {
          createCard(input: {
            pipe_id: $pipeId,
            phase_id: $phaseId,
            fields_attributes: $fieldsAttributes
          }) {
            card {
              id
              title
              current_phase {
                id
                name
              }
              fields {
                name
                value
              }
            }
          }
        }
        """
        variables = {
          "pipeId": payload.pipe_id,
          "phaseId": payload.phase_id,
          "fieldsAttributes": payload.fields_attributes,
        }
        return query, variables

    @staticmethod
    def delete_card(payload: DeleteCardInput) -> tuple[str, dict[str, Any]]:
        query = """
        mutation DeleteCard($cardId: ID!) {
          deleteCard(input: { id: $cardId }) {
            success
          }
        }
        """
        variables = {"cardId": payload.card_id}
        return query, variables

    @staticmethod
    def move_card_to_phase(payload: MoveCardToPhaseInput) -> tuple[str, dict[str, Any]]:
        query = """
        mutation MoveCardToPhase($cardId: ID!, $destinationPhaseId: ID!) {
          moveCardToPhase(
            input: {
              card_id: $cardId,
              destination_phase_id: $destinationPhaseId
            }
          ) {
            card {
              id
              current_phase {
                id
                name
              }
            }
          }
        }
        """
        variables = {
            "cardId": payload.card_id,
            "destinationPhaseId": payload.destination_phase_id,
        }
        return query, variables

    @staticmethod
    def fetch_pipe_phases(payload: FetchPipePhasesInput) -> tuple[str, dict[str, Any]]:
        query = """
        query FetchPipePhases($pipeId: ID!) {
          pipe(id: $pipeId) {
            id
            phases {
              id
              name
            }
          }
        }
        """
        variables = {"pipeId": payload.pipe_id}
        return query, variables