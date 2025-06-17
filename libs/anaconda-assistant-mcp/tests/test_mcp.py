import pytest
from fastmcp import FastMCP, Client
import asyncio

from anaconda_assistant_mcp.cli import mcp

# client = Client(mcp)


# @pytest.fixture(autouse=True)
# def setup():
#     # print("Available MCP methods:")
#     # for method in dir(mcp):
#     #     if not method.startswith("_"):
#     #         print(f"- {method}")
#     print(dir(mcp))
#     mcp.run(transport="stdio")


# def test_add():
#     assert mcp.add(1, 3) == 4


# @pytest.mark.asyncio
# async def test_add():
#     async with Client(mcp) as client:
#         result = await client.call_tool("add", {"1": "3"})
#         assert result[0].text == 4


# def test_mcp_add():
#     result = mcp.invoke_tool("add", {"a": 2, "b": 3})
#     assert result == 5


# def test_mcp_subtract():
#     result = mcp.invoke_tool("subtract", {"a": 2, "b": 3})
#     assert result == -1


# def test_mcp_list_packages():
#     result = mcp.invoke_tool("list_packages", {})
#     assert "# Name" in result
#     assert "Version" in result


# def test_mcp_list_pretend_packages():
#     result = mcp.invoke_tool("list_pretend_packages", {})
#     assert "# Name" in result


# def test_mcp_list_envs():
#     result = mcp.invoke_tool("list_envs", {})
#     assert "conda" in result or "base" in result
