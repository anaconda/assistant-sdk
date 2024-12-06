from uuid import uuid4
from typing import Callable, Any, List, Optional, Dict, Tuple
from warnings import warn

import ell
from ell.provider import EllCallParams, Provider, Metadata
from ell.types import Message, ContentBlock
from ell.types._lstr import _lstr

from anaconda_assistant.core import ChatClient, ChatResponse


class AnacondaAssistantProvider(Provider):
    def provider_call_function(
        self,
        client: ChatClient,
        api_call_params: Optional[Dict[str, Any]] = None,
    ) -> Callable[..., Any]:
        return client.completions

    def translate_to_provider(self, ell_call: EllCallParams) -> Dict[str, Any]:
        final_call_params = {}

        if ell_call.api_params.get("api_params", {}).get("stream", False):
            final_call_params["stream"] = ell_call.api_params.get("api_params", {}).get(
                "stream", False
            )

        converse_messages = [format_messages(message) for message in ell_call.messages]
        final_call_params["messages"] = converse_messages

        if ell_call.tools:
            warn("Tool calls not supported and are ignored")

        return final_call_params

    def translate_from_provider(
        self,
        provider_response: ChatResponse,
        ell_call: EllCallParams,
        provider_call_params: Dict[str, Any],
        origin_id: Optional[str] = None,
        logger: Optional[Callable[..., None]] = None,
    ) -> Tuple[List[Message], Metadata]:
        usage = {}
        metadata: Metadata = {}

        tracked_results: List[Message] = []
        did_stream = ell_call.api_params.get("api_params", {}).get("stream")

        content: list[ContentBlock] = []
        for chunk in provider_response.iter_content():
            content_block = ContentBlock(
                text=_lstr(content=chunk, origin_trace=origin_id)
            )
            content.append(content_block)
            if logger:
                logger(chunk)

        if not did_stream:
            content = ContentBlock(
                text=_lstr("".join(c.text for c in content), origin_trace=origin_id)  # type: ignore
            )
        message = Message(role="assistant", content=content)  # type: ignore
        tracked_results.append(message)

        usage["prompt_tokens"] = 0
        usage["completions_tokens"] = 0
        usage["total_tokens"] = provider_response.tokens_used
        metadata["usage"] = usage

        return tracked_results, metadata


def format_messages(message: Message) -> Dict[str, Any]:
    if message.images or message.audios or message.tool_calls or message.tool_results:
        warn("This message contains non-text content, which is ignored.")

    converse_message = {
        "role": message.role,
        "content": message.text_only,
        "message_id": str(uuid4()),
    }
    return converse_message


anaconda_assistant_provider = AnacondaAssistantProvider()

ell.register_provider(anaconda_assistant_provider, ChatClient)

client = ChatClient()

ell.config.register_model(
    name="anaconda-assistant", default_client=client, supports_streaming=True
)
