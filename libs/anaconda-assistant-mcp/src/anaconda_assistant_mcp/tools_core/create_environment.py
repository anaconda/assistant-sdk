import os
from typing import List, Optional

from conda.base.context import context
from conda.core.solve import Solver
from conda.core.envs_manager import register_env
from conda.models.match_spec import MatchSpec
from conda.models.channel import Channel


def create_environment_core(
    env_name: str,
    python_version: Optional[str] = None,
    packages: Optional[List[str]] = None,
    prefix: Optional[str] = None
) -> str:
    """
    Create a new conda environment using conda's internal APIs.
    Returns the full path to the created environment.
    """
    # Determine the environment path
    if prefix:
        env_path = prefix
    else:
        env_path = _get_default_env_path(env_name)
    
    # Create the environment directory if it doesn't exist
    os.makedirs(env_path, exist_ok=True)
    
    # Build the list of specs to install
    specs = []
    if python_version:
        specs.append(f"python={python_version}")
    if packages:
        specs.extend(packages)
    
    # If no specs provided, install python
    if not specs:
        specs = ["python"]
    
    # Convert specs to MatchSpec objects
    match_specs = [MatchSpec(spec) for spec in specs]
    
    # Convert string channels to Channel objects
    channels = [Channel(channel) for channel in context.channels]
    
    # Create solver
    solver = Solver(
        prefix=env_path,
        channels=channels,
        subdirs=[context.subdir],
        specs_to_add=match_specs
    )
    
    # Solve for the transaction
    transaction = solver.solve_for_transaction()
    
    # Execute the transaction
    transaction.execute()
    
    # Register the environment
    register_env(env_path)
    
    return env_path


def _get_default_env_path(env_name: str) -> str:
    """Get the default path for an environment with the given name."""
    return os.path.join(context.envs_dirs[0], env_name) 