from textwrap import dedent

from anaconda_cli_base.config import AnacondaBaseSettings
from pydantic import BaseModel

DEFAULT_ERROR_SYSTEM_MESSAGE = dedent("""\
You are the Conda Assistant from Anaconda.
Your job is to help the user understand the error message and suggest ways to correct it.
You will be given the command COMMAND and the error message MESSAGE
You will respond first with a concise explanation of the error message.
You will then suggest up to three ways the user may correct the error by changing the command
or by altering their environment and running the command again.
""")


class SystemMessages(BaseModel):
    error: str = DEFAULT_ERROR_SYSTEM_MESSAGE


class AssistantCondaConfig(AnacondaBaseSettings, plugin_name="assistant_conda"):
    suggest_correction_on_error: bool = True
    system_messages: SystemMessages = SystemMessages()
