from typing import Any
import pytest
from anaconda_assistant_mcp.experiments.server_experiments import add, subtract


@pytest.mark.asyncio
async def test_add() -> None:
    """Test that the anaconda assistant mcp is working."""
    assert await add(1, 2) == 3


@pytest.mark.asyncio
async def test_subtract() -> None:
    """Test that the anaconda assistant mcp is working."""
    assert await subtract(1, 2) == -1
