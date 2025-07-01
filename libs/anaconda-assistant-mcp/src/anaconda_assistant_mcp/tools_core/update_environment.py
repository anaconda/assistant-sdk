import os
from typing import List, Optional

from conda.base.context import context
from conda.core.solve import Solver
from conda.core.link import UnlinkLinkTransaction
from conda.models.match_spec import MatchSpec
from conda.models.channel import Channel
from conda.core.index import get_index


def update_environment_core(
    packages: List[str],
    env_name: Optional[str] = None,
    prefix: Optional[str] = None
) -> str:
    """
    Update an existing conda environment using conda's internal APIs.
    Returns the full path to the updated environment.
    """
    # Determine the environment path
    if prefix:
        env_path = prefix
    elif env_name:
        env_path = _get_default_env_path(env_name)
    else:
        raise ValueError("Either env_name or prefix must be provided.")
    
    # Verify the environment exists
    if not os.path.exists(env_path):
        raise ValueError(f"Environment does not exist: {env_path}")
    
    # Convert specs to MatchSpec objects
    match_specs = [MatchSpec(spec) for spec in packages]
    
    # Get the index for the channels
    index = get_index(
        channel_urls=context.channels,
        prepend=False,
        platform=context.subdir
    )
    
    # Convert string channels to Channel objects
    channels = [Channel(channel) for channel in context.channels]
    
    # Create solver for updating the environment
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
    
    return env_path


def _get_default_env_path(env_name: str) -> str:
    """Get the default path for an environment with the given name."""
    return os.path.join(context.envs_dirs[0], env_name) 