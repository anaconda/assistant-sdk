from textwrap import dedent

from anaconda_cli_base.config import AnacondaBaseSettings
from pydantic import BaseModel
from typing import Literal, Optional
from .core import set_config

DebugErrorMode = Optional[Literal["automatic", "ask", "off"]]

DEFAULT_ERROR_SYSTEM_MESSAGE = dedent(
    """\
You are the Conda Assistant from Anaconda.
Your job is to help the user understand the error message and suggest ways to correct it.
You will be given the command COMMAND and the error message MESSAGE
You will respond first with a concise explanation of the error message.
You will then suggest up to three ways the user may correct the error by changing the command
or by altering their environment and running the command again.
Make sure to quote packages with versions like so `conda create -n myenv \"anaconda-cloud-auth=0.7\" \"pydantic>=2.7.0\"`.
"""
)


class SystemMessages(BaseModel):
    error: str = DEFAULT_ERROR_SYSTEM_MESSAGE


class AssistantCondaConfig(AnacondaBaseSettings, plugin_name="assistant"):
    debug_error_mode: DebugErrorMode = None
    system_messages: SystemMessages = SystemMessages()


# NOTE: in the future, we'll want to make sure `set` and `get` API is mirrored for all keys, likely with a better API
# than `set_debug_error_mode()` and `get_debug_error_mode()`


def set_debug_error_mode(
    mode: DebugErrorMode,
) -> None:
    """Set the debug error mode in the config."""
    set_config("plugin.assistant", "debug_error_mode", mode)


def get_debug_error_mode() -> DebugErrorMode:
    """Get the debug error mode from the config."""
    return AssistantCondaConfig().debug_error_mode
