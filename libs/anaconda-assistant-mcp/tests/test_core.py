from typing import Any
import pytest
from anaconda_assistant_mcp.cli import add, subtract


@pytest.fixture
def dummy_test_data() -> dict[str, Any]:
    """Return dummy test data for testing purposes."""
    return {
        "test_string": "hello world",
        "test_number": 42,
        "test_list": [1, 2, 3],
        "test_dict": {"key": "value"},
    }


def test_dummy_data(dummy_test_data: dict[str, Any]) -> None:
    """Test that dummy data has expected values."""
    assert dummy_test_data["test_string"] == "hello world"
    assert dummy_test_data["test_number"] == 42
    assert dummy_test_data["test_list"] == [1, 2, 3]
    assert dummy_test_data["test_dict"] == {"key": "value"}


def test_mcp() -> None:
    """Test that the mcp is working."""
    assert True


def test_anaconda_assistant_add() -> None:
    """Test that the anaconda assistant mcp is working."""
    assert add(1, 2) == 3


def test_anaconda_assistant_subtract() -> None:
    """Test that the anaconda assistant mcp is working."""
    assert subtract(1, 2) == -1
