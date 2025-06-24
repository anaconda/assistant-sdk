import pytest
from fastmcp import Client
import json

from conda.core.envs_manager import list_all_known_prefixes
from anaconda_assistant_mcp.server import mcp


@pytest.fixture(autouse=True)
def setup() -> None:
    global client
    client = Client(mcp)


@pytest.mark.asyncio
async def test_list_environment_has_base() -> None:
    async with client:
        conda_result = await client.call_tool("list_environment", {})
        parsed_result = json.loads(conda_result[0].text)
        assert any(env["name"] == "base" for env in parsed_result)


@pytest.mark.asyncio
async def test_list_environment_has_all_envs() -> None:
    async with client:
        conda_result = await client.call_tool("list_environment", {})
        parsed_result = json.loads(conda_result[0].text)

        known_prefixes = list_all_known_prefixes()
        known_prefixes = sorted(known_prefixes)

        # Extract paths from parsed_result
        result_paths = [env["path"] for env in parsed_result]
        result_paths = sorted(result_paths)

        # Assert that both lists contain the same paths
        assert known_prefixes == result_paths
