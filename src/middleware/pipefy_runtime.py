import sys
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_module(module_name: str, file_path: Path):
    spec = spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {file_path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache
def get_pipefy_runtime_components():
    src_root = Path(__file__).resolve().parents[1]
    src_root_str = str(src_root)
    if src_root_str not in sys.path:
        sys.path.insert(0, src_root_str)

    client_module = _load_module(
        "pipefy_graphql_client_runtime",
        src_root / "pipefy_clients" / "pipefy_graphql_client.py",
    )
    builder_module = _load_module(
        "pipefy_operation_builder_runtime",
        src_root / "pipefy_clients" / "pipefy_operation_builder.py",
    )

    return (
        client_module.PipefyGraphQLClient,
        client_module.PipefyResponseParser,
        builder_module.PipefyOperationBuilder,
    )
