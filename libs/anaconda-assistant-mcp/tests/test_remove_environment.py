import os
import tempfile
import pytest
from typing import Generator
from unittest.mock import Mock, patch
from fastmcp import Client

from anaconda_assistant_mcp.tools_core.remove_environment import remove_environment_core
from anaconda_assistant_mcp.server import mcp

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_env_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing environment removal."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_context() -> Generator[Mock, None, None]:
    """Mock conda context for testing."""
    with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_ctx:
        with patch('anaconda_assistant_mcp.tools_core.shared.context', mock_ctx):
            mock_ctx.channels = ('defaults',)
            mock_ctx.subdir = 'linux-64'
            mock_ctx.envs_dirs = ['/tmp/conda/envs']
            mock_ctx.root_prefix = '/opt/anaconda3'  # Mock base environment path
            yield mock_ctx


@pytest.fixture
def mock_unregister_env() -> Generator[Mock, None, None]:
    """Mock unregister_env function."""
    with patch('anaconda_assistant_mcp.tools_core.remove_environment.unregister_env') as mock_unregister:
        yield mock_unregister


@pytest.fixture()
def client() -> Client:
    """FastMCP client for integration testing."""
    return Client(mcp)


# =============================================================================
# UNIT TESTS - Testing remove_environment_core function directly
# =============================================================================

class TestRemoveEnvironmentCore:
    """Unit tests for remove_environment_core function."""

    def test_remove_environment_core_by_name(self, temp_env_dir: str, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test environment removal by name."""
        env_name = "test_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        assert os.path.exists(env_path)
        
        result = remove_environment_core(env_name=env_name, prefix=env_path)
        
        assert result == env_path
        assert not os.path.exists(env_path)  # Directory should be removed
        mock_unregister_env.assert_called_once_with(env_path)

    def test_remove_environment_core_by_prefix(self, temp_env_dir: str, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test environment removal by prefix path."""
        env_path = os.path.join(temp_env_dir, "custom_env")
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        assert os.path.exists(env_path)
        
        result = remove_environment_core(prefix=env_path)
        
        assert result == env_path
        assert not os.path.exists(env_path)  # Directory should be removed
        mock_unregister_env.assert_called_once_with(env_path)

    def test_remove_environment_core_uses_default_path(self, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test that environment uses default path when only name is provided."""
        env_name = "test_env_default_path"
        expected_path = os.path.join(mock_context.envs_dirs[0], env_name)
        
        # Mock the environment to exist
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.os.path.exists', return_value=True):
            with patch('anaconda_assistant_mcp.tools_core.shared.os.path.exists', return_value=True):
                with patch('shutil.rmtree') as mock_rmtree:
                    result = remove_environment_core(env_name=env_name)
                    
                    assert result == expected_path
                    mock_unregister_env.assert_called_once_with(expected_path)
                    mock_rmtree.assert_called_once_with(expected_path)

    def test_remove_environment_core_environment_not_exists(self, temp_env_dir: str, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test that ValueError is raised when environment doesn't exist."""
        env_name = "nonexistent_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Ensure the environment doesn't exist
        assert not os.path.exists(env_path)
        
        with pytest.raises(ValueError, match="Environment does not exist"):
            remove_environment_core(env_name=env_name, prefix=env_path)

    def test_remove_environment_core_base_environment(self, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test that ValueError is raised when trying to remove base environment."""
        base_path = mock_context.root_prefix
        
        with patch('os.path.exists', return_value=True):
            with pytest.raises(ValueError, match="Cannot remove the base environment"):
                remove_environment_core(prefix=base_path)

    def test_remove_environment_core_no_name_or_prefix(self, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test that ValueError is raised when neither name nor prefix is provided."""
        with pytest.raises(ValueError, match="Either env_name or prefix must be provided"):
            remove_environment_core()

    def test_remove_environment_core_unregister_error(self, temp_env_dir: str, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test that RuntimeError is raised when unregister fails."""
        env_name = "test_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        
        # Make unregister_env raise an exception
        mock_unregister_env.side_effect = Exception("Unregister failed")
        
        with pytest.raises(RuntimeError, match="Failed to remove environment"):
            remove_environment_core(env_name=env_name, prefix=env_path)

    def test_remove_environment_core_rmtree_error(self, temp_env_dir: str, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test that RuntimeError is raised when directory removal fails."""
        env_name = "test_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        
        # Mock shutil.rmtree to raise an exception
        with patch('shutil.rmtree') as mock_rmtree:
            mock_rmtree.side_effect = Exception("Directory removal failed")
            
            with pytest.raises(RuntimeError, match="Failed to remove environment"):
                remove_environment_core(env_name=env_name, prefix=env_path)

    def test_remove_environment_core_directory_already_removed(self, temp_env_dir: str, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test that function works when directory is already removed."""
        env_name = "test_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        assert os.path.exists(env_path)
        
        # Mock os.path.exists to return False for the environment path
        # This simulates the directory being removed by another process
        def mock_exists(path: str) -> bool:
            if path == env_path:
                return False
            return os.path.exists(path)
        
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.os.path.exists', side_effect=mock_exists):
            with patch('anaconda_assistant_mcp.tools_core.shared.os.path.exists', side_effect=mock_exists):
                # This should raise ValueError because the environment doesn't exist
                with pytest.raises(ValueError, match="Environment does not exist"):
                    remove_environment_core(env_name=env_name, prefix=env_path)

    def test_remove_environment_core_handles_nested_directories(self, temp_env_dir: str, mock_context: Mock, mock_unregister_env: Mock) -> None:
        """Test that function can remove environments with nested directories."""
        env_name = "test_env_nested"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the environment directory with nested structure
        os.makedirs(os.path.join(env_path, "bin"), exist_ok=True)
        os.makedirs(os.path.join(env_path, "lib", "python3.9"), exist_ok=True)
        
        # Create some files
        with open(os.path.join(env_path, "bin", "python"), "w") as f:
            f.write("#!/bin/bash")
        
        assert os.path.exists(env_path)
        
        result = remove_environment_core(env_name=env_name, prefix=env_path)
        
        assert result == env_path
        assert not os.path.exists(env_path)  # Directory should be removed
        mock_unregister_env.assert_called_once_with(env_path)


# =============================================================================
# INTEGRATION TESTS - Testing remove_environment MCP tool
# =============================================================================

class TestRemoveEnvironmentIntegration:
    """Integration tests for the remove_environment MCP tool."""

    @pytest.mark.asyncio
    async def test_remove_environment_by_name(self, client: Client, temp_env_dir: str) -> None:
        """Test environment removal by name through MCP."""
        env_name = "test_mcp_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        assert os.path.exists(env_path)
        
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_context:
            mock_context.root_prefix = '/opt/anaconda3'
            
            with patch('anaconda_assistant_mcp.tools_core.remove_environment.unregister_env'):
                async with client:
                    result = await client.call_tool(
                        "remove_environment",
                        {
                            "env_name": env_name,
                            "prefix": env_path
                        }
                    )
                    
                    # Verify the result
                    assert result[0].text == env_path  # type: ignore[union-attr]
                    assert not os.path.exists(env_path)  # Directory should be removed

    @pytest.mark.asyncio
    async def test_remove_environment_by_prefix(self, client: Client, temp_env_dir: str) -> None:
        """Test environment removal by prefix through MCP."""
        env_path = os.path.join(temp_env_dir, "custom_mcp_env")
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        assert os.path.exists(env_path)
        
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_context:
            mock_context.root_prefix = '/opt/anaconda3'
            
            with patch('anaconda_assistant_mcp.tools_core.remove_environment.unregister_env'):
                async with client:
                    result = await client.call_tool(
                        "remove_environment",
                        {
                            "prefix": env_path
                        }
                    )
                    
                    # Verify the result
                    assert result[0].text == env_path  # type: ignore[union-attr]
                    assert not os.path.exists(env_path)  # Directory should be removed

    @pytest.mark.asyncio
    async def test_remove_environment_environment_not_exists(self, client: Client, temp_env_dir: str) -> None:
        """Test that error is raised when environment doesn't exist through MCP."""
        env_name = "nonexistent_mcp_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Ensure the environment doesn't exist
        assert not os.path.exists(env_path)
        
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_context:
            mock_context.root_prefix = '/opt/anaconda3'
            
            async with client:
                with pytest.raises(Exception) as exc_info:
                    await client.call_tool(
                        "remove_environment",
                        {
                            "env_name": env_name,
                            "prefix": env_path
                        }
                    )
                
                # Verify the error message contains the expected information
                error_text = str(exc_info.value)
                assert "Failed to remove conda environment" in error_text
                assert "Environment does not exist" in error_text

    @pytest.mark.asyncio
    async def test_remove_environment_base_environment(self, client: Client) -> None:
        """Test that error is raised when trying to remove base environment through MCP."""
        base_path = '/opt/anaconda3'
        
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_context:
            mock_context.root_prefix = base_path
            
            with patch('os.path.exists', return_value=True):
                async with client:
                    with pytest.raises(Exception) as exc_info:
                        await client.call_tool(
                            "remove_environment",
                            {
                                "prefix": base_path
                            }
                        )
                    
                    # Verify the error message contains the expected information
                    error_text = str(exc_info.value)
                    assert "Failed to remove conda environment" in error_text
                    assert "Cannot remove the base environment" in error_text

    @pytest.mark.asyncio
    async def test_remove_environment_no_name_or_prefix(self, client: Client) -> None:
        """Test that error is raised when neither name nor prefix is provided through MCP."""
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_context:
            mock_context.root_prefix = '/opt/anaconda3'
            
            async with client:
                with pytest.raises(Exception) as exc_info:
                    await client.call_tool(
                        "remove_environment",
                        {}
                    )
                
                # Verify the error message contains the expected information
                error_text = str(exc_info.value)
                assert "Failed to remove conda environment" in error_text
                assert "Either env_name or prefix must be provided" in error_text

    @pytest.mark.asyncio
    async def test_remove_environment_unregister_error(self, client: Client, temp_env_dir: str) -> None:
        """Test that error is raised when unregister fails through MCP."""
        env_name = "test_mcp_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_context:
            mock_context.root_prefix = '/opt/anaconda3'
            
            with patch('anaconda_assistant_mcp.tools_core.remove_environment.unregister_env') as mock_unregister:
                mock_unregister.side_effect = Exception("Unregister failed")
                
                async with client:
                    with pytest.raises(Exception) as exc_info:
                        await client.call_tool(
                            "remove_environment",
                            {
                                "env_name": env_name,
                                "prefix": env_path
                            }
                        )
                    
                    # Verify the error message contains the expected information
                    error_text = str(exc_info.value)
                    assert "Failed to remove conda environment" in error_text
                    assert "Unregister failed" in error_text

    @pytest.mark.asyncio
    async def test_remove_environment_rmtree_error(self, client: Client, temp_env_dir: str) -> None:
        """Test that error is raised when directory removal fails through MCP."""
        env_name = "test_mcp_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the environment directory
        os.makedirs(env_path, exist_ok=True)
        
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_context:
            mock_context.root_prefix = '/opt/anaconda3'
            
            with patch('anaconda_assistant_mcp.tools_core.remove_environment.unregister_env'):
                with patch('shutil.rmtree') as mock_rmtree:
                    mock_rmtree.side_effect = Exception("Directory removal failed")
                    
                    async with client:
                        with pytest.raises(Exception) as exc_info:
                            await client.call_tool(
                                "remove_environment",
                                {
                                    "env_name": env_name,
                                    "prefix": env_path
                                }
                            )
                        
                        # Verify the error message contains the expected information
                        error_text = str(exc_info.value)
                        assert "Failed to remove conda environment" in error_text
                        assert "Directory removal failed" in error_text

    @pytest.mark.asyncio
    async def test_remove_environment_uses_default_path(self, client: Client) -> None:
        """Test that environment uses default path when only name is provided through MCP."""
        env_name = "test_mcp_default_path"
        
        with patch('anaconda_assistant_mcp.tools_core.remove_environment.context') as mock_context:
            mock_context.root_prefix = '/opt/anaconda3'
            mock_context.envs_dirs = ['/tmp/conda/envs']
            
            with patch('os.path.exists', return_value=True):
                with patch('anaconda_assistant_mcp.tools_core.remove_environment.unregister_env'):
                    with patch('shutil.rmtree') as mock_rmtree:
                        async with client:
                            result = await client.call_tool(
                                "remove_environment",
                                {
                                    "env_name": env_name
                                }
                            )
                            
                            # Verify the result contains the expected environment name
                            result_path = result[0].text  # type: ignore[union-attr]
                            assert env_name in result_path
                            assert result_path.endswith(env_name)
                            
                            # Verify rmtree was called with the same path
                            mock_rmtree.assert_called_once_with(result_path) 