from typing import Any, Dict, Optional, Sequence, List, cast

from llama_index.core.llms.custom import CustomLLM
from llama_index.core.base.llms.types import (
    ChatMessage,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
    MessageRole,
)

from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms.callbacks import llm_completion_callback

from anaconda_assistant.core import ChatClient, ChatResponse


def messages_to_prompt(messages: Sequence[ChatMessage]) -> List[dict]:
    formatted = [
        {"role": msg.role, "content": msg.content, "message_id": f"{idx}"}
        for idx, msg in enumerate(messages)
    ]
    return formatted


class AnacondaAssistant(CustomLLM):
    def __init__(
        self,
        system_prompt: Optional[str] = None,
        example_messages: Optional[List[Dict[str, str]]] = None,
        domain: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        callback_manager: Optional[CallbackManager] = None,
    ) -> None:
        super().__init__(
            system_prompt=system_prompt,
            callback_manager=callback_manager,
            messages_to_prompt=messages_to_prompt,
        )
        self._model = ChatClient(
            system_message=self.system_prompt,
            example_messages=example_messages,
            domain=domain,
            api_key=api_key,
            api_version=api_version,
        )

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            model_name="anaconda-assistant",
            is_chat_model=True,
            is_function_calling_model=False,
            system_role=MessageRole.SYSTEM,
        )

    @classmethod
    def class_name(cls) -> str:
        return "AnacondaAssistant"

    def _complete(self, prompt: str, formatted: bool = False) -> ChatResponse:
        if formatted:
            messages = cast(List[dict], prompt)
        else:
            messages = [{"role": "user", "content": prompt, "message_id": "0"}]
        response = self._model.completions(messages=messages)
        return response

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        response = self._complete(prompt, formatted)
        return CompletionResponse(text=response.message)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        response = self._complete(prompt, formatted)
        full = ""
        for chunk in response.iter_content():
            full += chunk
            yield CompletionResponse(text=full, delta=chunk)
