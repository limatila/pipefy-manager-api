import unittest
from unittest.mock import patch

import requests

from src.gql_response_mappers.dtos.cards import CreateCardInput, FetchPipePhasesInput
from src.pipefy_clients.pipefy_graphql_client import (
    PipefyGraphQLClient,
    PipefyResponseParser,
)
from src.pipefy_clients.pipefy_operation_builder import PipefyOperationBuilder


class PipefyClientsTests(unittest.TestCase):
    def test_create_card_builder_uses_requested_pipe_id(self):
        payload = CreateCardInput(
            pipe_id="307116004",
            phase_id="phase-1",
            fields_attributes=[{"field_id": "name", "field_value": "Alice"}],
        )

        query, variables = PipefyOperationBuilder.create_card(payload)

        self.assertIn("mutation CreateCard", query)
        self.assertEqual("307116004", variables["pipeId"])

    def test_fetch_pipe_phases_builder_uses_pipe_id(self):
        payload = FetchPipePhasesInput(pipe_id="307116004")

        query, variables = PipefyOperationBuilder.fetch_pipe_phases(payload)

        self.assertIn("query FetchPipePhases", query)
        self.assertEqual({"pipeId": "307116004"}, variables)

    def test_response_parser_normalizes_invalid_payload(self):
        result = PipefyResponseParser.normalize([])  # type: ignore[arg-type]

        self.assertIsNone(result["data"])
        self.assertEqual(1, len(result["errors"]))

    def test_graphql_client_handles_transport_error(self):
        with patch("requests.post", side_effect=requests.RequestException("error")):
            client = PipefyGraphQLClient(endpoint="https://api.pipefy.com/graphql", token="x")
            result = client.execute("query { me { id } }")

        self.assertIsNone(result["data"])
        self.assertIn("transport error", result["errors"][0]["message"].lower())


if __name__ == "__main__":
    unittest.main()
