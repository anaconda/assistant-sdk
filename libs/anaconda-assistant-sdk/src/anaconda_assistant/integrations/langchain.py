from collections.abc import Iterator
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import cast
from uuid import uuid4

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.messages import BaseMessage
from langchain_core.messages import ChatMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_core.outputs import ChatGeneration

from anaconda_assistant.core import ChatClient

SUPPORTED_ROLES: List[str] = ["user", "assistant", "system"]


def _convert_message_to_dict(message: BaseMessage) -> Dict:
    """Converts message to a dict according to role"""
    content = cast(str, message.content)
    if isinstance(message, HumanMessage):
        return {"role": "user", "content": content, "message_id": str(uuid4())}
    elif isinstance(message, AIMessage):
        return {"role": "assistant", "content": content, "message_id": str(uuid4())}
    elif isinstance(message, SystemMessage):
        return {"role": "system", "content": content, "message_id": str(uuid4())}
    elif isinstance(message, ChatMessage) and message.role in SUPPORTED_ROLES:
        return {"role": message.role, "content": content, "message_id": str(uuid4())}
    else:
        supported = ",".join([role for role in SUPPORTED_ROLES])
        raise ValueError(
            f"""Received unsupported role.
            Supported roles for the LLaMa Foundation Model: {supported}"""
        )


def _format_messages(messages: List[BaseMessage]) -> List[dict]:
    chat_messages = [_convert_message_to_dict(message) for message in messages]

    return chat_messages


class AnacondaAssistant(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        """Returns the type of LLM."""
        return "anaconda-assistant"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        client = ChatClient(**kwargs)

        payload = _format_messages(messages)
        response = client.completions(messages=payload)

        content = response.message
        llm_output = {
            "tokens_used": response.tokens_used,
            "token_limit": response.token_limit,
        }
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))],
            llm_output=llm_output,
        )

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        client = ChatClient(**kwargs)

        payload = _format_messages(messages)
        response = client.completions(messages=payload)

        for delta in response.iter_content():
            if response.tokens_used:
                response_metadata = {
                    "tokens_used": response.tokens_used,
                    "token_limit": response.token_limit,
                }
            else:
                response_metadata = {}

            chunk = ChatGenerationChunk(
                message=AIMessageChunk(
                    content=delta,
                ),
                generation_info=response_metadata,
            )
            if run_manager is not None:
                run_manager.on_llm_new_token(token=delta, chunk=chunk)
            yield chunk
