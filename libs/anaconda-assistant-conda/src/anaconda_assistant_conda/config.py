from textwrap import dedent

from anaconda_cli_base.config import AnacondaBaseSettings
from pydantic import BaseModel
from typing import Literal, Optional

# Adding `"none"`` rather than `None` because otherwise getting config via env var gets confused:
# https://anaconda.github.io/anaconda-cli-base/#config-file
DebugErrorMode = Literal["automatic", "ask", "off", "none"]

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
    debug_error_mode: DebugErrorMode = "none"
    system_messages: SystemMessages = SystemMessages()
