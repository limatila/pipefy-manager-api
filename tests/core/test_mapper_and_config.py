import unittest
from unittest.mock import patch

import src.core.config as config_module

from src.dtos.cards import CardCreateRequest
from src.gql_response_mappers.cards_mapper import CardsMapper


class MapperAndConfigTests(unittest.TestCase):
    def test_pipe_id_target_is_supported_in_runtime_config(self):
        with patch.object(config_module, "PIPE_ID", "307116004"):
            self.assertEqual("307116004", config_module.PIPE_ID)

    def test_cards_mapper_uses_target_pipe_id(self):
        with patch("src.gql_response_mappers.cards_mapper.PIPE_ID", "307116004"):
            mapper = CardsMapper()
            payload = CardCreateRequest(
                name="Alice",
                email="alice@example.com",
                tax_id="123",
                phase_id="phase-1",
            )

            gql_input = mapper.to_create_card_input(payload)

            self.assertEqual("307116004", gql_input.pipe_id)
            self.assertEqual("phase-1", gql_input.phase_id)
            self.assertEqual(3, len(gql_input.fields_attributes))

    def test_cards_mapper_skips_none_optional_fields(self):
        mapper = CardsMapper()
        payload = CardCreateRequest(
            name="Alice",
            email="alice@example.com",
            tax_id=None,
            phase_id=None,
        )

        gql_input = mapper.to_create_card_input(payload)

        field_ids = {item["field_id"] for item in gql_input.fields_attributes}
        self.assertEqual({"name", "email"}, field_ids)


if __name__ == "__main__":
    unittest.main()
