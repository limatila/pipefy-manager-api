from src.dtos.lookup import PhaseResult, PhaseSearchResponse


class PhasesMapper:
    @staticmethod
    def from_pipe_phases(raw: dict, name_filter: str | None = None) -> PhaseSearchResponse:
        phases = (((raw.get("data") or {}).get("pipe") or {}).get("phases") or [])
        results = [
            PhaseResult(id=p["id"], name=p["name"])
            for p in phases
            if not name_filter or name_filter.lower() in p.get("name", "").lower()
        ]
        return PhaseSearchResponse(results=results)
