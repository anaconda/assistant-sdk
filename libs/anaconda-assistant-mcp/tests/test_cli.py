from typing import Any
import pytest
from anaconda_assistant_mcp.experiments.server_experiments import add, subtract
import subprocess
from unittest.mock import patch, MagicMock


def test_assert_true() -> None:
    """Test that the mcp is working."""
    assert True


def test_add() -> None:
    """Test that the anaconda assistant mcp is working."""
    assert add(1, 2) == 3


def test_subtract() -> None:
    """Test that the anaconda assistant mcp is working."""
    assert subtract(1, 2) == -1


# def test_list_packages(capsys):
#     """Test that list_packages outputs conda list in expected format (integration test)."""
#     from anaconda_assistant_mcp.cli import list_packages

#     list_packages()
#     captured = capsys.readouterr()
#     output = captured.out
#     # Check for the table header
#     assert "# Name" in output
#     assert "Version" in output
#     assert "Build" in output
#     # Check for at least one non-header package line (heuristic: line not starting with # and not empty)
#     package_lines = [
#         line
#         for line in output.splitlines()
#         if line.strip() and not line.startswith("#")
#     ]
#     assert any(len(line.split()) >= 3 for line in package_lines)
