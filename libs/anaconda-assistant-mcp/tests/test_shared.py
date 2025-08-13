"""
Shared test utilities for MCP tools.

This module contains common test functions and constants used across
multiple test modules to avoid code duplication.
"""

import pytest
from typing import List, Tuple
from unittest.mock import Mock


# =============================================================================
# ERROR MESSAGES
# =============================================================================

# Permission-related error messages that should be returned by MCP tools
PERMISSION_ERROR_MESSAGE = "Permission denied - check if you have write access to the environment location"

# Error message prefixes for different tools
CREATE_ENVIRONMENT_ERROR_PREFIX = "Failed to create conda environment"
REMOVE_ENVIRONMENT_ERROR_PREFIX = "Failed to remove conda environment"
UPDATE_ENVIRONMENT_ERROR_PREFIX = "Failed to update conda environment"

# =============================================================================
# TEST ERROR SCENARIOS
# =============================================================================

PERMISSION_ERROR_SCENARIOS = [
    ("PermissionError", PermissionError("Permission denied")),
    ("OSError Access Denied", OSError("Access denied")),
    ("OSError Insufficient Access Rights", OSError("Insufficient access rights")),
    ("OSError Permission Denied", OSError("Permission denied")),
    ("OSError EACCES", OSError(13, "Permission denied")),  # EACCES error code
    ("OSError EPERM", OSError(1, "Operation not permitted")),  # EPERM error code
]

# =============================================================================
# SHARED TEST FUNCTIONS
# =============================================================================

def assert_permission_error_message(error_text: str, expected_prefix: str) -> None:
    """
    Assert that an error message contains the expected permission error information.
    
    Args:
        error_text: The error message text to check
        expected_prefix: The expected error prefix for the specific tool
    """
    assert expected_prefix in error_text
    assert PERMISSION_ERROR_MESSAGE in error_text





# =============================================================================
# SHARED TEST HELPERS FOR MCP INTEGRATION TESTS
# =============================================================================

def setup_mock_context_for_permission_test(mock_context: Mock, temp_env_dir: str) -> None:
    """
    Set up mock context for permission error testing.
    
    Args:
        mock_context: Mock context object
        temp_env_dir: Temporary directory for testing
    """
    mock_context.channels = ('defaults',)
    mock_context.subdir = 'linux-64'
    mock_context.envs_dirs = [temp_env_dir]


def create_mock_solver_with_permission_error(mock_solver_cls: Mock, exception: Exception) -> Mock:
    """
    Create a mock solver that raises a permission error during transaction execution.
    
    Args:
        mock_solver_cls: Mock solver class
        exception: Exception to raise
        
    Returns:
        Mock solver instance
    """
    mock_solver = Mock()
    mock_transaction = Mock()
    mock_transaction.execute.side_effect = exception
    mock_solver.solve_for_transaction.return_value = mock_transaction
    mock_solver_cls.return_value = mock_solver
    return mock_solver


def create_mock_rmtree_with_permission_error(mock_rmtree: Mock, exception: Exception) -> None:
    """
    Create a mock rmtree that raises a permission error.
    
    Args:
        mock_rmtree: Mock rmtree function
        exception: Exception to raise
    """
    mock_rmtree.side_effect = exception


# =============================================================================
# PARAMETRIZED TEST DECORATORS
# =============================================================================

def parametrize_permission_errors():
    """
    Decorator to parametrize tests with different permission error scenarios.
    """
    test_cases = []
    for scenario_name, exception in PERMISSION_ERROR_SCENARIOS:
        error_message = str(exception)
        test_cases.append((scenario_name, error_message, exception))
    
    return pytest.mark.parametrize(
        "error_scenario_name,error_message,exception",
        test_cases,
        ids=[case[0] for case in test_cases]
    )
