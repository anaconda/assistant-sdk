from typing import Any
import pytest


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
