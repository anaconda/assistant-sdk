import pytest
from fastmcp import Client
import json

from conda.core.envs_manager import list_all_known_prefixes
from anaconda_assistant_mcp.server import mcp


@pytest.fixture()
def client() -> Client:
    return Client(mcp)


@pytest.mark.asyncio
async def test_list_environment_has_base(client: Client) -> None:
    async with client:
        conda_result = await client.call_tool("list_environment", {})
        parsed_result = json.loads(conda_result[0].text)  # type: ignore[union-attr]
        assert any(env["name"] == "base" for env in parsed_result)


@pytest.mark.asyncio
async def test_list_environment_has_all_envs(client: Client) -> None:
    async with client:
        conda_result = await client.call_tool("list_environment", {})
        parsed_result = json.loads(conda_result[0].text)  # type: ignore[union-attr]

        known_prefixes = list_all_known_prefixes()
        known_prefixes = sorted(known_prefixes)

        # Extract paths from parsed_result
        result_paths = [env["path"] for env in parsed_result]
        result_paths = sorted(result_paths)

        # Assert that both lists contain the same paths
        assert known_prefixes == result_paths


mock_query_all_response = [
    "conda-forge/osx-arm64::numpy==1.23.5=py310h5d7c261_0",
    "conda-forge/osx-arm64::numpy==1.23.5=py311ha92fb03_0",
]


@pytest.mark.asyncio
async def test_search_packages(monkeypatch: pytest.MonkeyPatch, client: Client) -> None:
    monkeypatch.setattr(
        "conda.api.SubdirData.query_all",
        lambda query, channels=None, subdirs=None: mock_query_all_response,
    )
    async with client:
        conda_result = await client.call_tool("search_packages", {"query": "numpy"})
        parsed_result = json.loads(conda_result[0].text)  # type: ignore[union-attr]
        assert parsed_result == mock_query_all_response
