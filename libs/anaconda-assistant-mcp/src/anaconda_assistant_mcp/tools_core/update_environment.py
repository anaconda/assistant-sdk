from typing import List, Optional

from conda.base.context import context
from conda.core.solve import Solver
from conda.core.link import UnlinkLinkTransaction
from conda.models.match_spec import MatchSpec
from conda.core.index import get_index
from conda.models.channel import Channel

from .shared import (
    resolve_environment_path,
    validate_environment_exists,
    get_channels_from_condarc
)


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
    env_path = resolve_environment_path(env_name=env_name, prefix=prefix)
    
    # Verify the environment exists
    validate_environment_exists(env_path)
    
    # Convert specs to MatchSpec objects
    match_specs = [MatchSpec(spec) for spec in packages]
    
    # Get the index for the channels
    index = get_index(
        channel_urls=get_channels_from_condarc(),
        prepend=False,
        platform=context.subdir
    )
    
    # Convert string channels to Channel objects
    channel_strings = get_channels_from_condarc()
    channels = [Channel(channel) for channel in channel_strings]
    
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


 