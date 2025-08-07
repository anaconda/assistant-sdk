import os
import sys
from typing import List, Optional

from conda.base.context import context, Context
from conda.api import Solver
from conda.core.envs_manager import register_env
from conda.models.match_spec import MatchSpec
from conda.models.channel import Channel

from .shared import (
    resolve_environment_path,
    get_channels_from_condarc,
    suppress_conda_output
)


def create_environment_core(
    env_name: str,
    packages: Optional[List[str]] = None,
    prefix: Optional[str] = None
) -> str:
    """
    Create a new conda environment using conda's internal APIs.
    Returns the full path to the created environment.
    """
    # Determine the environment path
    env_path = resolve_environment_path(env_name=env_name, prefix=prefix)
    
    # Create the environment directory if it doesn't exist
    os.makedirs(env_path, exist_ok=True)
    
    # Convert specs to MatchSpec objects
    match_specs = [MatchSpec(spec) for spec in packages]
    
    # Convert string channels to Channel objects
    channel_strings = get_channels_from_condarc()
    channels = [Channel(channel) for channel in channel_strings]
    
    # Create solver
    solver = Solver(
        prefix=env_path,
        channels=channels,
        subdirs=[context.subdir],
        specs_to_add=match_specs
    )
    
    # Execute conda operations with suppressed output to prevent MCP JSON interference
    with suppress_conda_output():
        # Solve for the transaction
        transaction = solver.solve_for_transaction()
        
        # Execute the transaction
        transaction.execute()
    
    # Register the environment
    register_env(env_path)
    
    return env_path


 