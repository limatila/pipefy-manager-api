import unittest

from src.middleware.pipefy_runtime import get_pipefy_runtime_components


class RuntimeIntegrityTests(unittest.TestCase):
    def test_runtime_components_are_resolved(self):
        client_cls, parser_cls, builder_cls = get_pipefy_runtime_components()

        self.assertEqual("PipefyGraphQLClient", client_cls.__name__)
        self.assertEqual("PipefyResponseParser", parser_cls.__name__)
        self.assertEqual("PipefyOperationBuilder", builder_cls.__name__)


if __name__ == "__main__":
    unittest.main()
