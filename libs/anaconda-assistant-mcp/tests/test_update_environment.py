import os
import tempfile
import pytest
import json
import re
from typing import Generator
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from fastmcp import Client

from conda.core.solve import Solver
from conda.core.link import UnlinkLinkTransaction
from conda.models.match_spec import MatchSpec
from conda.models.channel import Channel
from conda.base.context import context

from anaconda_assistant_mcp.tools_core.update_environment import update_environment_core
from anaconda_assistant_mcp.server import mcp
from anaconda_assistant_mcp.tools_core.shared import os

import sys

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_env_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing environment updates."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def existing_env_path(temp_env_dir: str) -> str:
    """Create a temporary environment directory that exists."""
    env_path = os.path.join(temp_env_dir, "existing_env")
    os.makedirs(env_path, exist_ok=True)
    return env_path


@pytest.fixture
def mock_context() -> Generator[Mock, None, None]:
    """Mock conda context for testing."""
    with patch('anaconda_assistant_mcp.tools_core.update_environment.context') as mock_ctx:
        with patch('anaconda_assistant_mcp.tools_core.shared.context', mock_ctx):
            mock_ctx.channels = ('defaults',)
            mock_ctx.subdir = 'linux-64'
            mock_ctx.envs_dirs = ['/tmp/conda/envs']
            yield mock_ctx


@pytest.fixture
def mock_solver() -> Generator[Mock, None, None]:
    """Mock Solver class."""
    with patch('anaconda_assistant_mcp.tools_core.update_environment.Solver') as mock_solver_cls:
        mock_solver = Mock()
        mock_transaction = Mock()
        mock_solver.solve_for_transaction.return_value = mock_transaction
        mock_solver_cls.return_value = mock_solver
        yield mock_solver_cls


@pytest.fixture
def mock_get_index() -> Generator[Mock, None, None]:
    """Mock get_index function."""
    with patch('anaconda_assistant_mcp.tools_core.update_environment.get_index') as mock_index:
        yield mock_index


@pytest.fixture()
def client() -> Client:
    """FastMCP client for integration testing."""
    return Client(mcp)


# =============================================================================
# UNIT TESTS - Testing update_environment_core function directly
# =============================================================================

class TestUpdateEnvironmentCore:
    """Unit tests for update_environment_core function."""

    def test_update_environment_core_basic(self, existing_env_path: str, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test basic environment update."""
        packages = ["numpy>=1.20", "pandas"]
        
        # Mock get_channels_from_condarc to return expected channels
        with patch('anaconda_assistant_mcp.tools_core.update_environment.get_channels_from_condarc') as mock_get_channels:
            mock_get_channels.return_value = ['conda-forge', 'defaults', 'pkgs/main', 'pkgs/r']
            
            result = update_environment_core(
                packages=packages,
                prefix=existing_env_path
            )
        
        assert result == existing_env_path
        
        # Verify Solver was called with correct parameters
        mock_solver.assert_called_once()
        call_args = mock_solver.call_args
        assert call_args[1]['prefix'] == existing_env_path
        assert call_args[1]['subdirs'] == ['linux-64']
        
        # Verify specs were converted to MatchSpec objects
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 2
        assert specs[0].name == 'numpy'
        assert specs[0].version == '>=1.20'
        assert specs[1].name == 'pandas'
        
        # Verify channels were converted to Channel objects
        channels = call_args[1]['channels']
        assert len(channels) == 4
        assert all(isinstance(ch, Channel) for ch in channels)
        assert channels[0].name == 'conda-forge'
        assert channels[1].name == 'defaults'
        assert channels[2].name == 'pkgs/main'
        assert channels[3].name == 'pkgs/r'
        
        # Verify get_index was called
        mock_get_index.assert_called_once_with(
            channel_urls=['conda-forge', 'defaults', 'pkgs/main', 'pkgs/r'],
            prepend=False,
            platform='linux-64'
        )

    def test_update_environment_core_with_env_name(self, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test environment update using environment name."""
        packages = ["numpy>=1.20", "pandas"]
        env_name = "test_env"
        
        # Mock os.path.exists to return True for the expected path
        expected_path = os.path.join('/tmp/conda/envs', env_name)
        with patch('anaconda_assistant_mcp.tools_core.shared.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            result = update_environment_core(
                packages=packages,
                env_name=env_name
            )
            
            assert result == expected_path
            
            # Verify Solver was called with the expected path
            call_args = mock_solver.call_args
            assert call_args[1]['prefix'] == expected_path
            
            # Verify specs were converted properly
            specs = call_args[1]['specs_to_add']
            assert len(specs) == 2
            assert specs[0].name == 'numpy'
            assert str(specs[0].version) == '>=1.20'
            assert specs[1].name == 'pandas'

    def test_update_environment_core_with_complex_packages(self, existing_env_path: str, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test environment update with complex package specifications."""
        packages = ["numpy>=1.20,<2.0", "pandas=1.5.*", "matplotlib"]
        
        result = update_environment_core(
            packages=packages,
            prefix=existing_env_path
        )
        
        assert result == existing_env_path
        
        # Verify specs were converted properly
        call_args = mock_solver.call_args
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 3
        
        # Check numpy spec
        numpy_spec = next(s for s in specs if s.name == 'numpy')
        assert str(numpy_spec.version) == '>=1.20,<2.0'
        
        # Check pandas spec
        pandas_spec = next(s for s in specs if s.name == 'pandas')
        assert str(pandas_spec.version) == '1.5.*'
        
        # Check matplotlib spec
        matplotlib_spec = next(s for s in specs if s.name == 'matplotlib')
        assert matplotlib_spec.version is None  # No version constraint

    def test_update_environment_core_empty_packages(self, existing_env_path: str, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test environment update with empty packages list."""
        packages: list[str] = []
        
        result = update_environment_core(
            packages=packages,
            prefix=existing_env_path
        )
        
        assert result == existing_env_path
        
        # Verify Solver was called with empty specs
        call_args = mock_solver.call_args
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 0

    def test_update_environment_core_missing_env_name_and_prefix(self, mock_context: Mock) -> None:
        """Test that ValueError is raised when neither env_name nor prefix is provided."""
        packages = ["numpy"]
        
        with pytest.raises(ValueError, match="Either env_name or prefix must be provided"):
            update_environment_core(packages=packages)

    def test_update_environment_core_nonexistent_env_prefix(self, temp_env_dir: str, mock_context: Mock) -> None:
        """Test that ValueError is raised when environment doesn't exist."""
        packages = ["numpy"]
        nonexistent_path = os.path.join(temp_env_dir, "nonexistent_env")
        
        with pytest.raises(ValueError, match=re.escape(f"Environment does not exist: {nonexistent_path}")):
            update_environment_core(
                packages=packages,
                prefix=nonexistent_path
            )

    def test_update_environment_core_nonexistent_env_name(self, mock_context: Mock) -> None:
        """Test that ValueError is raised when environment name doesn't exist."""
        packages = ["numpy"]
        env_name = "nonexistent_env"
        
        # Mock os.path.exists to return False for the specific path
        expected_path = os.path.join('/tmp/conda/envs', env_name)
        with patch('anaconda_assistant_mcp.tools_core.shared.os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            with pytest.raises(ValueError, match=re.escape(f"Environment does not exist: {expected_path}")):
                update_environment_core(
                    packages=packages,
                    env_name=env_name
                )

    def test_update_environment_core_solver_error(self, existing_env_path: str, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test that solver errors are properly propagated."""
        packages = ["numpy"]
        
        # Make the solver raise an exception
        mock_solver_instance = mock_solver.return_value
        mock_solver_instance.solve_for_transaction.side_effect = Exception("Solver failed")
        
        with pytest.raises(Exception, match="Solver failed"):
            update_environment_core(
                packages=packages,
                prefix=existing_env_path
            )

    def test_update_environment_core_transaction_error(self, existing_env_path: str, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test that transaction execution errors are properly propagated."""
        packages = ["numpy"]
        
        # Make the transaction execution raise an exception
        mock_solver_instance = mock_solver.return_value
        mock_transaction = Mock()
        mock_transaction.execute.side_effect = Exception("Transaction failed")
        mock_solver_instance.solve_for_transaction.return_value = mock_transaction
        
        with pytest.raises(Exception, match="Transaction failed"):
            update_environment_core(
                packages=packages,
                prefix=existing_env_path
            )

    def test_update_environment_core_channel_conversion(self, existing_env_path: str, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test that string channels are properly converted to Channel objects."""
        packages = ["numpy"]
        
        # Mock get_channels_from_condarc to return custom channels
        with patch('anaconda_assistant_mcp.tools_core.update_environment.get_channels_from_condarc') as mock_get_channels:
            mock_get_channels.return_value = ['custom-channel', 'another-channel']
            
            result = update_environment_core(
                packages=packages,
                prefix=existing_env_path
            )
            
            assert result == existing_env_path
            
            # Verify channels were converted to Channel objects
            call_args = mock_solver.call_args
            channels = call_args[1]['channels']
            assert len(channels) == 2
            assert all(isinstance(ch, Channel) for ch in channels)
            assert channels[0].name == 'custom-channel'
            assert channels[1].name == 'another-channel'
            
            # Verify get_index was called with the correct channels
            mock_get_index.assert_called_once_with(
                channel_urls=['custom-channel', 'another-channel'],
                prepend=False,
                platform='linux-64'
            )

    def test_update_environment_core_matchspec_conversion(self, existing_env_path: str, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test that package strings are properly converted to MatchSpec objects."""
        packages = ["numpy>=1.20", "pandas=1.5.*", "matplotlib"]
        
        result = update_environment_core(
            packages=packages,
            prefix=existing_env_path
        )
        
        assert result == existing_env_path
        
        # Verify specs were converted to MatchSpec objects
        call_args = mock_solver.call_args
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 3
        assert all(isinstance(spec, MatchSpec) for spec in specs)
        
        # Verify specific specs
        numpy_spec = next(s for s in specs if s.name == 'numpy')
        assert numpy_spec.name == 'numpy'
        assert str(numpy_spec.version) == '>=1.20'
        
        pandas_spec = next(s for s in specs if s.name == 'pandas')
        assert pandas_spec.name == 'pandas'
        assert str(pandas_spec.version) == '1.5.*'
        
        matplotlib_spec = next(s for s in specs if s.name == 'matplotlib')
        assert matplotlib_spec.name == 'matplotlib'
        assert matplotlib_spec.version is None

    def test_update_environment_core_priority_env_name_over_prefix(self, existing_env_path: str, mock_context: Mock, mock_solver: Mock, mock_get_index: Mock) -> None:
        """Test that prefix takes priority when both env_name and prefix are provided."""
        packages = ["numpy"]
        env_name = "test_env"
        
        result = update_environment_core(
            packages=packages,
            env_name=env_name,
            prefix=existing_env_path
        )
        
        # Should use the prefix, not the env_name
        assert result == existing_env_path
        
        # Verify Solver was called with the prefix path
        call_args = mock_solver.call_args
        assert call_args[1]['prefix'] == existing_env_path


# =============================================================================
# INTEGRATION TESTS - Testing update_environment MCP tool
# =============================================================================

class TestUpdateEnvironmentIntegration:
    """Integration tests for the update_environment MCP tool."""

    @pytest.mark.asyncio
    async def test_update_environment_basic(self, client: Client, existing_env_path: str) -> None:
        """Test basic environment update through MCP."""
        packages = ["numpy", "pandas"]
        
        with patch('anaconda_assistant_mcp.tools_core.update_environment.context') as mock_context:
            mock_context.channels = ('defaults', 'conda-forge')
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = ['/tmp/conda/envs']
            
            with patch('anaconda_assistant_mcp.tools_core.update_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.update_environment.get_index'):
                    async with client:
                        result = await client.call_tool(
                            "update_environment",
                            {
                                "packages": packages,
                                "prefix": existing_env_path
                            }
                        )
                        
                        # Verify the result
                        assert result[0].text == existing_env_path  # type: ignore[union-attr]
                        
                        # Verify the solver was called
                        mock_solver_cls.assert_called_once()
                        mock_solver.solve_for_transaction.assert_called_once()
                        mock_transaction.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_environment_with_env_name(self, client: Client) -> None:
        """Test environment update using environment name through MCP."""
        packages = ["numpy>=1.20", "pandas"]
        env_name = "test_env"
        
        with patch('anaconda_assistant_mcp.tools_core.update_environment.context') as mock_context:
            with patch('anaconda_assistant_mcp.tools_core.shared.context', mock_context):
                mock_context.channels = ('defaults',)
                mock_context.subdir = 'linux-64'
                mock_context.envs_dirs = ['/tmp/conda/envs']
                
                with patch('anaconda_assistant_mcp.tools_core.update_environment.Solver') as mock_solver_cls:
                    mock_solver = Mock()
                    mock_transaction = Mock()
                    mock_solver.solve_for_transaction.return_value = mock_transaction
                    mock_solver_cls.return_value = mock_solver
                    
                    with patch('anaconda_assistant_mcp.tools_core.update_environment.get_index'):
                        with patch('anaconda_assistant_mcp.tools_core.shared.os.path.exists') as mock_exists:
                            mock_exists.return_value = True
                            
                            async with client:
                                result = await client.call_tool(
                                    "update_environment",
                                    {
                                        "packages": packages,
                                        "env_name": env_name
                                    }
                                )
                                
                                expected_path = os.path.join('/tmp/conda/envs', env_name)
                                assert result[0].text == expected_path  # type: ignore[union-attr]
                                
                                # Verify the solver was called with the expected path
                                call_args = mock_solver_cls.call_args
                                assert call_args[1]['prefix'] == expected_path

    @pytest.mark.asyncio
    async def test_update_environment_with_complex_packages(self, client: Client, existing_env_path: str) -> None:
        """Test environment update with complex package specifications through MCP."""
        packages = ["numpy>=1.20,<2.0", "pandas=1.5.*", "matplotlib"]
        
        with patch('anaconda_assistant_mcp.tools_core.update_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = ['/tmp/conda/envs']
            
            with patch('anaconda_assistant_mcp.tools_core.update_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.update_environment.get_index'):
                    async with client:
                        result = await client.call_tool(
                            "update_environment",
                            {
                                "packages": packages,
                                "prefix": existing_env_path
                            }
                        )
                        
                        # Verify the result
                        assert result[0].text == existing_env_path  # type: ignore[union-attr]
                        
                        # Verify the solver was called with correct specs
                        call_args = mock_solver_cls.call_args
                        specs = call_args[1]['specs_to_add']
                        assert len(specs) == 3
                        
                        # Check numpy spec
                        numpy_spec = next(s for s in specs if s.name == 'numpy')
                        assert str(numpy_spec.version) == '>=1.20,<2.0'
                        # Check pandas spec
                        pandas_spec = next(s for s in specs if s.name == 'pandas')
                        assert str(pandas_spec.version) == '1.5.*'
                        # Check matplotlib spec
                        matplotlib_spec = next(s for s in specs if s.name == 'matplotlib')
                        assert matplotlib_spec.version is None

    @pytest.mark.asyncio
    async def test_update_environment_empty_packages(self, client: Client, existing_env_path: str) -> None:
        """Test environment update with empty packages list through MCP."""
        packages: list[str] = []
        
        from fastmcp.exceptions import ToolError
        with pytest.raises(ToolError) as exc_info:
            async with client:
                await client.call_tool(
                    "update_environment",
                    {
                        "packages": packages,
                        "prefix": existing_env_path
                    }
                )
        error_text = str(exc_info.value)
        assert "Must specify at least one package to update/install." in error_text

    @pytest.mark.asyncio
    async def test_update_environment_missing_parameters(self, client: Client) -> None:
        """Test that appropriate error is raised when neither env_name nor prefix is provided."""
        packages = ["numpy"]
        
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "update_environment",
                    {
                        "packages": packages
                    }
                )
            
            # Verify the error message contains the expected information
            error_text = str(exc_info.value)
            assert "Either env_name or prefix must be provided" in error_text

    @pytest.mark.asyncio
    async def test_update_environment_nonexistent_env(self, client: Client, temp_env_dir: str) -> None:
        """Test that appropriate error is raised when environment doesn't exist."""
        packages = ["numpy"]
        nonexistent_path = os.path.join(temp_env_dir, "nonexistent_env")
        
        async with client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "update_environment",
                    {
                        "packages": packages,
                        "prefix": nonexistent_path
                    }
                )
            
            # Verify the error message contains the expected information
            error_text = str(exc_info.value)
            assert "Environment does not exist" in error_text

    @pytest.mark.asyncio
    async def test_update_environment_solver_error(self, client: Client, existing_env_path: str) -> None:
        """Test that solver errors are properly handled and reported through MCP."""
        packages = ["numpy"]
        
        with patch('anaconda_assistant_mcp.tools_core.update_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = ['/tmp/conda/envs']
            
            with patch('anaconda_assistant_mcp.tools_core.update_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_solver.solve_for_transaction.side_effect = Exception("UnsatisfiableError: Package dependency conflicts")
                mock_solver_cls.return_value = mock_solver
                
                async with client:
                    with pytest.raises(Exception) as exc_info:
                        await client.call_tool(
                            "update_environment",
                            {
                                "packages": packages,
                                "prefix": existing_env_path
                            }
                        )
                    
                    # Verify the error message contains the expected information
                    error_text = str(exc_info.value)
                    assert "Conda update failed:" in error_text
                    assert "Package dependency conflicts" in error_text

    @pytest.mark.asyncio
    async def test_update_environment_transaction_error(self, client: Client, existing_env_path: str) -> None:
        """Test that transaction execution errors are properly handled through MCP."""
        packages = ["numpy"]
        
        with patch('anaconda_assistant_mcp.tools_core.update_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = ['/tmp/conda/envs']
            
            with patch('anaconda_assistant_mcp.tools_core.update_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_transaction.execute.side_effect = Exception("Permission denied")
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                async with client:
                    with pytest.raises(Exception) as exc_info:
                        await client.call_tool(
                            "update_environment",
                            {
                                "packages": packages,
                                "prefix": existing_env_path
                            }
                        )
                    
                    # Verify the error message contains the expected information
                    error_text = str(exc_info.value)
                    assert "Conda update failed:" in error_text
                    assert "Permission denied" in error_text

    @pytest.mark.asyncio
    async def test_update_environment_priority_prefix_over_env_name(self, client: Client, existing_env_path: str) -> None:
        """Test that prefix takes priority when both env_name and prefix are provided through MCP."""
        packages = ["numpy"]
        env_name = "test_env"
        
        with patch('anaconda_assistant_mcp.tools_core.update_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = ['/tmp/conda/envs']
            
            with patch('anaconda_assistant_mcp.tools_core.update_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.update_environment.get_index'):
                    with patch('anaconda_assistant_mcp.tools_core.shared.os.path.exists') as mock_exists:
                        mock_exists.return_value = True
                        
                        async with client:
                            result = await client.call_tool(
                                "update_environment",
                                {
                                    "packages": packages,
                                    "env_name": env_name,
                                    "prefix": existing_env_path
                                }
                            )
                            
                            # Should use the prefix, not the env_name
                            assert result[0].text == existing_env_path  # type: ignore[union-attr]
                            
                            # Verify Solver was called with the prefix path
                            call_args = mock_solver_cls.call_args
                            assert call_args[1]['prefix'] == existing_env_path 