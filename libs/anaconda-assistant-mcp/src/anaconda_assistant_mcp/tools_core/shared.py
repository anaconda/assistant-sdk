"""
Shared utilities for conda environment management tools.

This module contains common functions and utilities used across
multiple tools_core modules to avoid code duplication.
"""

import os
import sys
import subprocess
from typing import List, Optional, Tuple
from conda.base.context import context
from conda.models.channel import Channel


def get_default_env_path(env_name: str) -> str:
    """
    Get the default path for an environment with the given name.
    
    Args:
        env_name: Name of the environment
        
    Returns:
        Full path to the environment directory
    """
    return os.path.join(context.envs_dirs[0], env_name)


def resolve_environment_path(env_name: Optional[str] = None, prefix: Optional[str] = None) -> str:
    """
    Resolve the environment path from either env_name or prefix.
    
    Args:
        env_name: Optional environment name
        prefix: Optional full path to environment
        
    Returns:
        Resolved environment path
        
    Raises:
        ValueError: If neither env_name nor prefix is provided
    """
    if prefix:
        return prefix
    elif env_name:
        return get_default_env_path(env_name)
    else:
        raise ValueError("Either env_name or prefix must be provided.")


def validate_environment_exists(env_path: str) -> None:
    """
    Validate that the environment directory exists.
    
    Args:
        env_path: Path to the environment
        
    Raises:
        ValueError: If the environment does not exist
    """
    if not os.path.exists(env_path):
        raise ValueError(f"Environment does not exist: {env_path}")


def get_channels_from_context() -> List[Channel]:
    """
    Get Channel objects from the conda context.
    
    Returns:
        List of Channel objects
    """
    return [Channel(channel) for channel in context.channels]


def get_python_version_from_env(env_prefix: str) -> str:
    """
    Attempt to get the Python version from the environment's python executable.
    
    Args:
        env_prefix: Path to the environment
        
    Returns:
        Python version string or empty string if not found
    """
    if sys.platform == "win32":
        python_bin = os.path.join(env_prefix, "Scripts", "python.exe")
    else:
        python_bin = os.path.join(env_prefix, "bin", "python")
    
    if not os.path.exists(python_bin):
        return ""
    
    try:
        output = subprocess.check_output([python_bin, "--version"], stderr=subprocess.STDOUT)
        return output.decode().strip().split()[-1]
    except Exception:
        return ""


def get_channels_from_condarc() -> List[str]:
    """
    Attempt to get channels from the user's .condarc file.
    
    Returns:
        List of channel names
    """
    channels = []
    try:
        condarc_path = os.path.join(os.path.expanduser("~"), ".condarc")
        if os.path.exists(condarc_path):
            import yaml  # type: ignore
            with open(condarc_path, "r") as f:
                condarc = yaml.safe_load(f)
                channels = condarc.get("channels", [])
    except Exception:
        pass
    return channels


def get_env_info(env_path: str) -> dict:
    """
    Get basic information about a conda environment.
    
    Args:
        env_path: Path to the environment
        
    Returns:
        Dictionary with environment information
    """
    # Get environment name
    env_name = os.path.basename(env_path)
    if env_name == "":
        env_name = os.path.basename(os.path.dirname(env_path))

    # Check if this is the base environment
    is_base = env_path == context.root_prefix
    if is_base:
        env_name = "base"

    return {
        "name": env_name,
        "path": env_path,
    }


def build_package_specs(python_version: Optional[str] = None, packages: Optional[List[str]] = None) -> List[str]:
    """
    Build a list of package specifications for environment creation.
    
    Args:
        python_version: Optional Python version specification
        packages: Optional list of package specifications
        
    Returns:
        List of package specifications
    """
    specs = []
    
    if python_version:
        specs.append(f"python={python_version}")
    if packages:
        specs.extend(packages)
    
    # If no specs provided, install python
    if not specs:
        specs = ["python"]
    
    return specs