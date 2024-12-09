from typing import Optional, cast

from pandasai.llm.base import LLM
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.prompts.base import BasePrompt

from anaconda_assistant.core import ChatSession


class AnacondaAssistant(LLM):
    api_token: str

    @property
    def type(self) -> str:
        return "anaconda-assistant"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.session = ChatSession(api_key=api_key)

    def call(
        self, instruction: BasePrompt, context: Optional[PipelineContext] = None
    ) -> str:
        self.last_prompt = instruction.to_string()

        text = self.session.chat(self.last_prompt, stream=False)
        return cast(str, text)
