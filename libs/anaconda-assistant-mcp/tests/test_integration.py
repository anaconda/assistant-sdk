import sys
import pytest
from fastmcp import Client
import json

from conda.core.envs_manager import list_all_known_prefixes
from anaconda_assistant_mcp.server import mcp

# NOTE: Would love to call underlying function directly, but the @mcp.tool() decorator
# seems to prevent access to the underlying function.
# And docs say to test this way:
# https://gofastmcp.com/patterns/testing
# In any case, this is a good test of the MCP server.


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
        conda_result = await client.call_tool(
            "search_packages", {"package_name": "numpy"}
        )
        parsed_result = json.loads(conda_result[0].text)  # type: ignore[union-attr]
        assert parsed_result == mock_query_all_response


@pytest.mark.asyncio
async def test_show_environment_details(monkeypatch: pytest.MonkeyPatch, client: Client) -> None:
    async with client:
        monkeypatch.setattr(
            "conda.core.prefix_data.PrefixData.iter_records",
            lambda self: [type('Record', (), {'name': 'numpy'})()],
        )
        monkeypatch.setattr(
            "anaconda_assistant_mcp.tools_core.environment_details.get_python_version_from_env",
            lambda env_prefix: "3.2.1",
        )
        monkeypatch.setattr(
            "anaconda_assistant_mcp.tools_core.environment_details.get_channels_from_condarc",
            lambda: ["conda-forge"],
        )
        conda_result = await client.call_tool("show_environment_details", {"env_name": "base"})
        parsed_result = json.loads(conda_result[0].text)  # type: ignore[union-attr]
        assert parsed_result["python_version"] == "3.2.1"
        assert parsed_result["packages"] == ["numpy"]
        assert parsed_result["channels"] == ["conda-forge"]
