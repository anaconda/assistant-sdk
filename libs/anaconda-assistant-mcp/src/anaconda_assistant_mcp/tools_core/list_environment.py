from conda.base.context import context
from conda.core.envs_manager import list_all_known_prefixes

from .shared import get_env_info


def list_environment_core() -> list[dict]:
    # Get all known environment prefixes
    env_prefixes = list_all_known_prefixes()

    if not env_prefixes:
        return []

    # Sort environments for consistent output
    env_prefixes = sorted(env_prefixes)

    output = []
    for env_path in env_prefixes:
        output.append(get_env_info(env_path))

    return output



