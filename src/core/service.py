

from src.core.config import (
    PIPEFY_TOKEN,
    PIPEFY_GRAPHQL_ENDPOINT,
    PIPEFY_GRAPHQL_TIMEOUT_SECONDS,
)
from src.middleware.pipefy_runtime import get_pipefy_runtime_components


class BaseService:
    def __init__(self, mapper = None):
        self.mapper = mapper

    @staticmethod
    def _normalize_response(payload: dict) -> dict:
        _, parser_cls, _ = get_pipefy_runtime_components()
        return parser_cls.normalize(payload)

    @staticmethod
    def _builder_cls():
        _, _, builder_cls = get_pipefy_runtime_components()
        return builder_cls

    @staticmethod
    def _client():
        client_cls, _, _ = get_pipefy_runtime_components()
        return client_cls(
            endpoint=PIPEFY_GRAPHQL_ENDPOINT,
            token=PIPEFY_TOKEN,
            timeout=PIPEFY_GRAPHQL_TIMEOUT_SECONDS,
        )

    @staticmethod
    def _raise_if_pipefy_errors(normalized: dict):
        errors = normalized.get("errors", [])
        if errors:
            first_error = errors[0] if isinstance(errors[0], dict) else {"message": str(errors[0])}
            raise ValueError(first_error.get("message", "Pipefy error"))
