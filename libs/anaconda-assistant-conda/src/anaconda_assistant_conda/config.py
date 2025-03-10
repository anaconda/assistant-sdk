from textwrap import dedent

from anaconda_cli_base.config import AnacondaBaseSettings
from pydantic import BaseModel

DEFAULT_SEARCH_SYSTEM_MESSAGE = dedent("""\
You are the Conda Assistant from Anaconda.
Your job is to help find useful pip or conda packages that can achieve the outcome requested.
Do not respond directly to the input.
You will respond first with the name of the packages and then on a new line the command to install them.
You prefer to use conda and the defaults channel. Never install from conda-forge. Never install from pip.
You will provide a short description.
You will provide a single example block of code.
""")

DEFAULT_ERROR_SYSTEM_MESSAGE = dedent("""\
You are the Conda Assistant from Anaconda.
Your job is to help the user understand the error message and suggest ways to correct it.
You will be given the command COMMAND and the error message MESSAGE
You will respond first with a concise explanation of the error message.
You will then suggest up to three ways the user may correct the error by changing the command
or by altering their environment and running the command again.
""")


class SystemMessages(BaseModel):
    search: str = DEFAULT_SEARCH_SYSTEM_MESSAGE
    error: str = DEFAULT_ERROR_SYSTEM_MESSAGE


class AssistantCondaConfig(AnacondaBaseSettings, plugin_name="assistant_conda"):
    suggest_correction_on_error: bool = True
    system_messages: SystemMessages = SystemMessages()
