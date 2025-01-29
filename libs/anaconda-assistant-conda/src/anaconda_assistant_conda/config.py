from textwrap import dedent
from typing import Any
from warnings import warn

from anaconda_cli_base.config import AnacondaBaseSettings
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from anaconda_assistant_conda.exceptions import IncorrectModelClass

DEFAULT_SEARCH_SYSTEM_MESSAGE = dedent("""\
You are the Conda Assistant from Anaconda.
Your job is to help find useful pip or conda packages that can achieve the outcome requested.
Do not respond directly to the input.
You will respond first with the name of the package and the command to install it.
You prefer to use conda and the defaults channel. Do not install from conda-forge unless absolutely necessary.
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


class LLM(BaseModel):
    driver: str
    params: dict[str, Any] = Field(default_factory=dict)

    def load(self) -> BaseChatModel:
        if self.driver != DEFAULT_LLM.driver:
            warn("Loading a custom LLM is an experimental feature. Use with caution.")
        from importlib import import_module

        mod, object = self.driver.rsplit(":", maxsplit=1)
        module = import_module(mod)
        driver = getattr(module, object)
        if not issubclass(driver, BaseChatModel):
            raise IncorrectModelClass(
                f"{self.driver} is not a subclass of langchain BaseChatModel"
            )
        llm = driver(**self.params)
        return llm


DEFAULT_LLM = LLM(
    driver="anaconda_assistant.integrations.langchain:AnacondaAssistant", params={}
)


class AssistantCondaConfig(AnacondaBaseSettings, plugin_name="assistant_conda"):
    llm: LLM = DEFAULT_LLM
    suggest_correction_on_error: bool = True
    system_messages: SystemMessages = SystemMessages()
