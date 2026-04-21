from typing import Any

import requests

from src.core.config import PIPEFY_TOKEN


class PipefyGraphQLClient:
    def __init__(self, endpoint: str, token: str = PIPEFY_TOKEN, timeout: float = 30.0):
        if not endpoint:
            raise ValueError("Pipefy endpoint is required")
        if not token:
            raise ValueError("Pipefy token is required")

        self.endpoint = endpoint
        self.token = token
        self.timeout = timeout

    def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {
            "query": query,
            "variables": variables or {},
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
        
        except requests.RequestException as exc:
            return {
                "data": None,
                "errors": [{"message": f"Pipefy transport error: {exc}"}],
            }

        if response.status_code >= 400:
            return {
                "data": None,
                "errors": [
                    {
                        "message": f"Pipefy returned HTTP {response.status_code}",
                        "response": self._safe_json(response),
                    }
                ],
            }

        return self._decode_payload(response)

    @staticmethod
    def _decode_payload(response: requests.Response) -> dict[str, Any]:
        try:
            return response.json()
        except ValueError:
            return {
                "data": None,
                "errors": [{"message": "Pipefy response is not valid JSON"}],
            }

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text


class PipefyResponseParser:
    @staticmethod
    def normalize(payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {
                "data": None,
                "errors": [{"message": "Could not decode Pipefy response."}],
            }

        errors = payload.get("errors", [])
        if errors is None:
            errors = []
        if not isinstance(errors, list):
            errors = [{"message": "Could not decode Pipefy response."}]

        return {
            "data": payload.get("data"),
            "errors": errors,
        }


# Backward-compatible alias used by previous revisions.
PipefyRequestClient = PipefyGraphQLClient
