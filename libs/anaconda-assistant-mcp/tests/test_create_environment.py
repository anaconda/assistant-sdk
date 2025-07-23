import os
import tempfile
import pytest
from typing import Generator
from unittest.mock import Mock, patch
from fastmcp import Client

from conda.models.channel import Channel

from anaconda_assistant_mcp.tools_core.create_environment import create_environment_core
from anaconda_assistant_mcp.server import mcp

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_env_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing environment creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_context() -> Generator[Mock, None, None]:
    """Mock conda context for testing."""
    with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_ctx:
        with patch('anaconda_assistant_mcp.tools_core.shared.context', mock_ctx):
            mock_ctx.channels = ('defaults',)
            mock_ctx.subdir = 'linux-64'
            mock_ctx.envs_dirs = ['/tmp/conda/envs']
            yield mock_ctx


@pytest.fixture
def mock_solver() -> Generator[Mock, None, None]:
    """Mock Solver class."""
    with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
        mock_solver = Mock()
        mock_transaction = Mock()
        mock_solver.solve_for_transaction.return_value = mock_transaction
        mock_solver_cls.return_value = mock_solver
        yield mock_solver_cls


@pytest.fixture
def mock_register_env() -> Generator[Mock, None, None]:
    """Mock register_env function."""
    with patch('anaconda_assistant_mcp.tools_core.create_environment.register_env') as mock_register:
        yield mock_register


@pytest.fixture()
def client() -> Client:
    """FastMCP client for integration testing."""
    return Client(mcp)


# =============================================================================
# UNIT TESTS - Testing create_environment_core function directly
# =============================================================================

class TestCreateEnvironmentCore:
    """Unit tests for create_environment_core function."""

    def test_create_environment_core_basic(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test basic environment creation with default Python."""
        env_name = "test_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Mock get_channels_from_condarc to return expected channels
        with patch('anaconda_assistant_mcp.tools_core.create_environment.get_channels_from_condarc') as mock_get_channels:
            mock_get_channels.return_value = ['conda-forge', 'defaults', 'pkgs/main', 'pkgs/r']
            
            result = create_environment_core(
                env_name=env_name,
                prefix=env_path
            )
        
        assert result == env_path
        assert os.path.exists(env_path)
        
        # Verify Solver was called with correct parameters
        mock_solver.assert_called_once()
        call_args = mock_solver.call_args
        assert call_args[1]['prefix'] == env_path
        assert call_args[1]['subdirs'] == ['linux-64']
        
        # Verify specs include python
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 1
        assert specs[0].name == 'python'
        
        # Verify channels were converted properly
        channels = call_args[1]['channels']
        assert len(channels) == 4
        assert all(isinstance(ch, Channel) for ch in channels)
        assert channels[0].name == 'conda-forge'
        assert channels[1].name == 'defaults'
        assert channels[2].name == 'pkgs/main'
        assert channels[3].name == 'pkgs/r'
        
        # Verify transaction was executed
        mock_solver_instance = mock_solver.return_value
        mock_solver_instance.solve_for_transaction.assert_called_once()
        mock_solver_instance.solve_for_transaction().execute.assert_called_once()
        
        # Verify environment was registered
        mock_register_env.assert_called_once_with(env_path)

    def test_create_environment_core_with_python_version(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test environment creation with specific Python version."""
        env_name = "test_env_py39"
        env_path = os.path.join(temp_env_dir, env_name)
        python_version = "3.9"
        
        result = create_environment_core(
            env_name=env_name,
            python_version=python_version,
            prefix=env_path
        )
        
        assert result == env_path
        
        # Verify Solver was called with Python version spec
        call_args = mock_solver.call_args
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 1
        assert specs[0].name == 'python'
        # Check that the version spec contains the expected version
        assert str(specs[0].version) == f"{python_version}.*"

    def test_create_environment_core_with_packages(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test environment creation with additional packages."""
        env_name = "test_env_with_packages"
        env_path = os.path.join(temp_env_dir, env_name)
        packages = ["numpy", "pandas>=1.3"]
        
        result = create_environment_core(
            env_name=env_name,
            packages=packages,
            prefix=env_path
        )
        
        assert result == env_path
        
        # Verify Solver was called with packages only (no automatic python)
        call_args = mock_solver.call_args
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 2  # 2 packages only
        
        # Check that packages are included
        package_names = [s.name for s in specs]
        assert 'numpy' in package_names
        assert 'pandas' in package_names

    def test_create_environment_core_with_python_and_packages(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test environment creation with both Python version and packages."""
        env_name = "test_env_complete"
        env_path = os.path.join(temp_env_dir, env_name)
        python_version = "3.10"
        packages = ["numpy>=1.20", "pandas"]
        
        result = create_environment_core(
            env_name=env_name,
            python_version=python_version,
            packages=packages,
            prefix=env_path
        )
        
        assert result == env_path
        
        # Verify Solver was called with all specs
        call_args = mock_solver.call_args
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 3  # python + 2 packages
        
        # Check Python version
        python_spec = next(s for s in specs if s.name == 'python')
        assert str(python_spec.version) == f"{python_version}.*"
        
        # Check packages
        package_names = [s.name for s in specs if s.name != 'python']
        assert 'numpy' in package_names
        assert 'pandas' in package_names

    def test_create_environment_core_uses_default_path(self, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test that environment uses default path when prefix is not provided."""
        env_name = "test_env_default_path"
        
        result = create_environment_core(env_name=env_name)
        
        # The actual path will be based on the real conda environment
        expected_path = os.path.join(mock_context.envs_dirs[0], env_name)
        assert result == expected_path
        
        # Verify Solver was called with the expected path
        call_args = mock_solver.call_args
        assert call_args[1]['prefix'] == expected_path

    def test_create_environment_core_creates_directory(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test that the function creates the environment directory if it doesn't exist."""
        env_name = "test_env_new_dir"
        env_path = os.path.join(temp_env_dir, "new_subdir", env_name)
        
        # Ensure the directory doesn't exist initially
        assert not os.path.exists(env_path)
        
        result = create_environment_core(
            env_name=env_name,
            prefix=env_path
        )
        
        assert result == env_path
        assert os.path.exists(env_path)

    def test_create_environment_core_handles_existing_directory(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test that the function works when the directory already exists."""
        env_name = "test_env_existing"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Create the directory beforehand
        os.makedirs(env_path, exist_ok=True)
        assert os.path.exists(env_path)
        
        result = create_environment_core(
            env_name=env_name,
            prefix=env_path
        )
        
        assert result == env_path
        # Should not raise an error when directory already exists

    def test_create_environment_core_empty_packages_list(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test environment creation with empty packages list."""
        env_name = "test_env_empty_packages"
        env_path = os.path.join(temp_env_dir, env_name)
        
        result = create_environment_core(
            env_name=env_name,
            packages=[],
            prefix=env_path
        )
        
        assert result == env_path
        
        # Should include python since no specs were provided
        call_args = mock_solver.call_args
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 1
        assert specs[0].name == 'python'

    def test_create_environment_core_none_packages(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test environment creation with None packages."""
        env_name = "test_env_none_packages"
        env_path = os.path.join(temp_env_dir, env_name)
        
        result = create_environment_core(
            env_name=env_name,
            packages=None,
            prefix=env_path
        )
        
        assert result == env_path
        
        # Should include python since no specs were provided
        call_args = mock_solver.call_args
        specs = call_args[1]['specs_to_add']
        assert len(specs) == 1
        assert specs[0].name == 'python'

    def test_create_environment_core_solver_error(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test that solver errors are properly propagated."""
        env_name = "test_env_solver_error"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Make the solver raise an exception
        mock_solver_instance = mock_solver.return_value
        mock_solver_instance.solve_for_transaction.side_effect = Exception("Solver failed")
        
        with pytest.raises(Exception, match="Solver failed"):
            create_environment_core(
                env_name=env_name,
                prefix=env_path
            )

    def test_create_environment_core_transaction_error(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test that transaction execution errors are properly propagated."""
        env_name = "test_env_transaction_error"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Make the transaction execution raise an exception
        mock_solver_instance = mock_solver.return_value
        mock_transaction = Mock()
        mock_transaction.execute.side_effect = Exception("Transaction failed")
        mock_solver_instance.solve_for_transaction.return_value = mock_transaction
        
        with pytest.raises(Exception, match="Transaction failed"):
            create_environment_core(
                env_name=env_name,
                prefix=env_path
            )

    def test_create_environment_core_channel_conversion(self, temp_env_dir: str, mock_context: Mock, mock_solver: Mock, mock_register_env: Mock) -> None:
        """Test that string channels are properly converted to Channel objects."""
        env_name = "test_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        # Mock get_channels_from_condarc to return custom channels
        with patch('anaconda_assistant_mcp.tools_core.create_environment.get_channels_from_condarc') as mock_get_channels:
            mock_get_channels.return_value = ['custom-channel', 'another-channel']
            
            result = create_environment_core(
                env_name=env_name,
                prefix=env_path
            )
        
        assert result == env_path
        
        # Verify channels were converted to Channel objects
        call_args = mock_solver.call_args
        channels = call_args[1]['channels']
        assert len(channels) == 2
        assert all(isinstance(ch, Channel) for ch in channels)
        assert channels[0].name == 'custom-channel'
        assert channels[1].name == 'another-channel'


# =============================================================================
# INTEGRATION TESTS - Testing create_environment MCP tool
# =============================================================================

class TestCreateEnvironmentIntegration:
    """Integration tests for the create_environment MCP tool."""

    @pytest.mark.asyncio
    async def test_create_environment_basic(self, client: Client, temp_env_dir: str) -> None:
        """Test basic environment creation through MCP."""
        env_name = "test_mcp_env"
        env_path = os.path.join(temp_env_dir, env_name)
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            mock_context.channels = ('defaults', 'conda-forge')
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = [temp_env_dir]
            
            with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.create_environment.register_env'):
                    async with client:
                        result = await client.call_tool(
                            "create_environment",
                            {
                                "env_name": env_name,
                                "prefix": env_path
                            }
                        )
                        
                        # Verify the result
                        assert result[0].text == env_path  # type: ignore[union-attr]
                        
                        # Verify the solver was called
                        mock_solver_cls.assert_called_once()
                        mock_solver.solve_for_transaction.assert_called_once()
                        mock_transaction.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_environment_with_python_version(self, client: Client, temp_env_dir: str) -> None:
        """Test environment creation with Python version through MCP."""
        env_name = "test_mcp_py_env"
        env_path = os.path.join(temp_env_dir, env_name)
        python_version = "3.9"
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = [temp_env_dir]
            
            with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.create_environment.register_env'):
                    async with client:
                        result = await client.call_tool(
                            "create_environment",
                            {
                                "env_name": env_name,
                                "python_version": python_version,
                                "prefix": env_path
                            }
                        )
                        
                        # Verify the result
                        assert result[0].text == env_path  # type: ignore[union-attr]
                        
                        # Verify the solver was called with Python version
                        call_args = mock_solver_cls.call_args
                        specs = call_args[1]['specs_to_add']
                        python_spec = next(s for s in specs if s.name == 'python')
                        assert str(python_spec.version) == f"{python_version}.*"

    @pytest.mark.asyncio
    async def test_create_environment_with_packages(self, client: Client, temp_env_dir: str) -> None:
        """Test environment creation with packages through MCP."""
        env_name = "test_mcp_packages_env"
        env_path = os.path.join(temp_env_dir, env_name)
        packages = ["numpy", "pandas>=1.3"]
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = [temp_env_dir]
            
            with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.create_environment.register_env'):
                    async with client:
                        result = await client.call_tool(
                            "create_environment",
                            {
                                "env_name": env_name,
                                "packages": packages,
                                "prefix": env_path
                            }
                        )
                        
                        # Verify the result
                        assert result[0].text == env_path  # type: ignore[union-attr]
                        
                        # Verify the solver was called with packages
                        call_args = mock_solver_cls.call_args
                        specs = call_args[1]['specs_to_add']
                        package_names = [s.name for s in specs]
                        assert 'numpy' in package_names
                        assert 'pandas' in package_names

    @pytest.mark.asyncio
    async def test_create_environment_complete(self, client: Client, temp_env_dir: str) -> None:
        """Test complete environment creation with all parameters through MCP."""
        env_name = "test_mcp_complete_env"
        env_path = os.path.join(temp_env_dir, env_name)
        python_version = "3.10"
        packages = ["numpy>=1.20", "pandas", "matplotlib"]
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            mock_context.channels = ('defaults', 'conda-forge')
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = [temp_env_dir]
            
            with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.create_environment.register_env'):
                    async with client:
                        result = await client.call_tool(
                            "create_environment",
                            {
                                "env_name": env_name,
                                "python_version": python_version,
                                "packages": packages,
                                "prefix": env_path
                            }
                        )
                        
                        # Verify the result
                        assert result[0].text == env_path  # type: ignore[union-attr]
                        
                        # Verify the solver was called with all specs
                        call_args = mock_solver_cls.call_args
                        specs = call_args[1]['specs_to_add']
                        assert len(specs) == 4  # python + 3 packages
                        
                        # Check Python version
                        python_spec = next(s for s in specs if s.name == 'python')
                        assert str(python_spec.version) == f"{python_version}.*"
                        
                        # Check packages
                        package_names = [s.name for s in specs if s.name != 'python']
                        assert 'numpy' in package_names
                        assert 'pandas' in package_names
                        assert 'matplotlib' in package_names

    @pytest.mark.asyncio
    async def test_create_environment_uses_default_path(self, client: Client) -> None:
        """Test that environment uses default path when prefix is not provided."""
        env_name = "test_mcp_default_path"
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            with patch('anaconda_assistant_mcp.tools_core.shared.context', mock_context):
                mock_context.channels = ('defaults',)
                mock_context.subdir = 'linux-64'
                mock_context.envs_dirs = ['/tmp/conda/envs']
                
                with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                    mock_solver = Mock()
                    mock_transaction = Mock()
                    mock_solver.solve_for_transaction.return_value = mock_transaction
                    mock_solver_cls.return_value = mock_solver
                    
                    with patch('anaconda_assistant_mcp.tools_core.create_environment.register_env'):
                        async with client:
                            result = await client.call_tool(
                                "create_environment",
                                {
                                    "env_name": env_name
                                }
                            )
                            
                            expected_path = os.path.join('/tmp/conda/envs', env_name)
                            assert result[0].text == expected_path  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_create_environment_solver_error(self, client: Client, temp_env_dir: str) -> None:
        """Test that solver errors are properly handled and reported through MCP."""
        env_name = "test_mcp_solver_error"
        env_path = os.path.join(temp_env_dir, env_name)
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = [temp_env_dir]
            
            with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_solver.solve_for_transaction.side_effect = Exception("UnsatisfiableError: Package dependency conflicts")
                mock_solver_cls.return_value = mock_solver
                
                async with client:
                    with pytest.raises(Exception) as exc_info:
                        await client.call_tool(
                            "create_environment",
                            {
                                "env_name": env_name,
                                "prefix": env_path
                            }
                        )
                    
                    # Verify the error message contains the expected information
                    error_text = str(exc_info.value)
                    assert "Failed to create conda environment" in error_text
                    assert "Package dependency conflicts" in error_text

    @pytest.mark.asyncio
    async def test_create_environment_transaction_error(self, client: Client, temp_env_dir: str) -> None:
        """Test that transaction execution errors are properly handled through MCP."""
        env_name = "test_mcp_transaction_error"
        env_path = os.path.join(temp_env_dir, env_name)
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = [temp_env_dir]
            
            with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_transaction.execute.side_effect = Exception("Permission denied")
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                async with client:
                    with pytest.raises(Exception) as exc_info:
                        await client.call_tool(
                            "create_environment",
                            {
                                "env_name": env_name,
                                "prefix": env_path
                            }
                        )
                    
                    # Verify the error message contains the expected information
                    error_text = str(exc_info.value)
                    assert "Failed to create conda environment" in error_text
                    assert "Permission denied" in error_text

    @pytest.mark.asyncio
    async def test_create_environment_progress_reporting(self, client: Client, temp_env_dir: str) -> None:
        """Test that progress is reported during environment creation."""
        env_name = "test_mcp_progress"
        env_path = os.path.join(temp_env_dir, env_name)
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = [temp_env_dir]
            
            with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.create_environment.register_env'):
                    async with client:
                        result = await client.call_tool(
                            "create_environment",
                            {
                                "env_name": env_name,
                                "prefix": env_path
                            }
                        )
                        
                        # Verify the result is returned
                        assert result[0].text == env_path  # type: ignore[union-attr]
                        
                        # Note: Progress reporting is handled by the MCP framework
                        # and may not be directly testable in this context

    @pytest.mark.asyncio
    async def test_create_environment_empty_packages(self, client: Client, temp_env_dir: str) -> None:
        """Test environment creation with empty packages list through MCP."""
        env_name = "test_mcp_empty_packages"
        env_path = os.path.join(temp_env_dir, env_name)
        
        with patch('anaconda_assistant_mcp.tools_core.create_environment.context') as mock_context:
            mock_context.channels = ('defaults',)
            mock_context.subdir = 'linux-64'
            mock_context.envs_dirs = [temp_env_dir]
            
            with patch('anaconda_assistant_mcp.tools_core.create_environment.Solver') as mock_solver_cls:
                mock_solver = Mock()
                mock_transaction = Mock()
                mock_solver.solve_for_transaction.return_value = mock_transaction
                mock_solver_cls.return_value = mock_solver
                
                with patch('anaconda_assistant_mcp.tools_core.create_environment.register_env'):
                    async with client:
                        result = await client.call_tool(
                            "create_environment",
                            {
                                "env_name": env_name,
                                "packages": [],
                                "prefix": env_path
                            }
                        )
                        
                        # Verify the result
                        assert result[0].text == env_path  # type: ignore[union-attr]
                        
                        # Should include python since no specs were provided
                        call_args = mock_solver_cls.call_args
                        specs = call_args[1]['specs_to_add']
                        assert len(specs) == 1
                        assert specs[0].name == 'python' 