from src.core.service import BaseService
from src.dtos.lookup import CitySearchResponse
from src.gql_response_mappers.dtos.cards import FetchTableRecordsInput
from src.gql_response_mappers.cities_mapper import CitiesMapper


class CityService(BaseService):
    def __init__(self, mapper: CitiesMapper | None = None):
        self.mapper = mapper or CitiesMapper()

    def search_cities(self, name: str) -> CitySearchResponse:
        builder = self._builder_cls()
        client = self._client()
        query, variables = builder.fetch_table_records(FetchTableRecordsInput())
        normalized = self._normalize_response(client.execute(query, variables))
        self._raise_if_pipefy_errors(normalized)
        return self.mapper.from_table_records(normalized, name_filter=name)
