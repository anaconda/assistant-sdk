import os

from conda.base.context import context
from conda.core.envs_manager import list_all_known_prefixes


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


def get_env_info(env_path: str) -> dict:
    """Print information about a single environment"""
    # Get environment name
    env_name = os.path.basename(env_path)
    if env_name == "":
        env_name = os.path.basename(os.path.dirname(env_path))

    # Check if this is the base environment
    is_base = env_path == context.root_prefix
    if is_base:
        env_name = "base"

    # Check if environment exists and is accessible
    # exists = os.path.exists(env_path)
    # is_accessible = os.access(env_path, os.R_OK) if exists else False

    output = {
        "name": env_name,
        "path": env_path,
    }

    return output
