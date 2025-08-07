import os
import shutil
from typing import Optional

from conda.base.context import context
from conda.core.envs_manager import unregister_env

from .shared import (
    resolve_environment_path,
    validate_environment_exists
)


def remove_environment_core(
    env_name: Optional[str] = None,
    prefix: Optional[str] = None
) -> str:
    """
    Remove a conda environment using conda's internal APIs.
    Returns the full path to the removed environment.
    
    Args:
        env_name: Optional name of the environment to remove
        prefix: Optional full path to the environment to remove
        
    Returns:
        The full path to the removed environment
        
    Raises:
        ValueError: If neither env_name nor prefix is provided, or if environment doesn't exist
        RuntimeError: If environment removal fails
    """
    # Determine the environment path
    env_path = resolve_environment_path(env_name=env_name, prefix=prefix)
    
    # Validate that the environment exists
    validate_environment_exists(env_path)
    
    # Check if this is the base environment (should not be removed)
    if env_path == context.root_prefix:
        raise ValueError("Cannot remove the base environment")
    
    try:
        # Unregister the environment from conda's environment list
        unregister_env(env_path)
        
        # Remove the environment directory
        if os.path.exists(env_path):
            shutil.rmtree(env_path)
        
        return env_path
    except Exception as e:
        raise RuntimeError(f"Failed to remove environment '{env_path}': {str(e)}") 