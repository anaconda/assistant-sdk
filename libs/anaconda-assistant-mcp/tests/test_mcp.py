import pytest
from fastmcp import Client
import json

from anaconda_assistant_mcp.experiments.server_experiments import mcp


@pytest.fixture(autouse=True)
def setup():
    global client
    client = Client(mcp)


@pytest.mark.asyncio
async def test_add():
    async with client:
        result = await client.call_tool("add", {"a": 1, "b": 3})
        assert result[0].text == "4"


@pytest.mark.asyncio
async def test_list_envs_has_base():
    async with client:
        conda_result = await client.call_tool("list_envs", {})
        parsed_result = json.loads(conda_result[0].text)
        assert any(env["name"] == "base" for env in parsed_result)
