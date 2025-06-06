from typing import Any
import pytest
from anaconda_assistant_mcp.cli import add, subtract


def test_assert_true() -> None:
    """Test that the mcp is working."""
    assert True


def test_add() -> None:
    """Test that the anaconda assistant mcp is working."""
    assert add(1, 2) == 3


def test_subtract() -> None:
    """Test that the anaconda assistant mcp is working."""
    assert subtract(1, 2) == -1
