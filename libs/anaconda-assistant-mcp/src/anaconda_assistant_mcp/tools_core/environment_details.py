from typing import Optional
from conda.base.context import context
from conda.core.prefix_data import PrefixData
from conda.base.context import locate_prefix_by_name

from .shared import (
    resolve_environment_path,
    get_python_version_from_env,
    get_channels_from_condarc
)


def show_environment_details_core(env_name: Optional[str] = None, prefix: Optional[str] = None) -> dict:
    """Show installed packages and metadata for a given Conda environment."""
    # Determine the prefix (path) to the environment
    if prefix:
        env_prefix = str(prefix)
    elif env_name:
        if env_name == "base":
            env_prefix = str(context.root_prefix)
        else:
            try:
                env_prefix = str(locate_prefix_by_name(env_name))
            except Exception:
                raise ValueError(f"Environment not found: {env_name}")
    else:
        raise ValueError("Either env_name or prefix must be provided.")

    # Get installed packages
    try:
        prefix_data = PrefixData(env_prefix)
        packages = [rec.name for rec in prefix_data.iter_records()]
    except Exception:
        packages = []

    # Get python version
    python_version = get_python_version_from_env(str(env_prefix))

    # Get channels (not always available, so best effort)
    channels = get_channels_from_condarc()

    return {
        "packages": packages,
        "python_version": python_version,
        "channels": channels,
    }

