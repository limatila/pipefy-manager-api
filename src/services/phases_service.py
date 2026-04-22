from src.core.service import BaseService
from src.dtos.lookup import PhaseSearchResponse
from src.gql_response_mappers.dtos.cards import FetchPipePhasesInput
from src.gql_response_mappers.phases_mapper import PhasesMapper


class PhaseService(BaseService):
    def __init__(self, mapper: PhasesMapper | None = None):
        self.mapper = mapper or PhasesMapper()

    def search_phases(self, name: str | None = None) -> PhaseSearchResponse:
        builder = self._builder_cls()
        client = self._client()
        query, variables = builder.fetch_pipe_phases(FetchPipePhasesInput())
        normalized = self._normalize_response(client.execute(query, variables))
        self._raise_if_pipefy_errors(normalized)
        return self.mapper.from_pipe_phases(normalized, name_filter=name)
