from src.dtos.lookup import CityResult, CitySearchResponse


class CitiesMapper:
    @staticmethod
    def from_table_records(raw: dict, name_filter: str) -> CitySearchResponse:
        edges = (((raw.get("data") or {}).get("table_records") or {}).get("edges") or [])
        results = [
            CityResult(id=e["node"]["id"], name=e["node"]["title"])
            for e in edges
            if e.get("node") and name_filter.lower() in (e["node"].get("title") or "").lower()
        ]
        return CitySearchResponse(results=results)
