from typing import Iterator, Union, Callable
from uuid import uuid4

import llm

from anaconda_assistant.core import ChatClient


@llm.hookimpl
def register_models(register: Callable) -> None:
    register(AnacondaAssistantChat())


class AnacondaAssistantChat(llm.Model):
    can_stream: bool = True
    model_id = "anaconda-assistant"

    def __str__(self) -> str:
        return f"AnacondaAssistant Chat: {self.model_id}"

    def execute(
        self,
        prompt: llm.Prompt,
        stream: bool,
        response: llm.Response,
        conversation: Union[llm.Conversation, None],
    ) -> Iterator[str]:
        messages = self.build_messages(prompt, conversation)
        response._prompt_json = {"messages": messages}

        client = ChatClient()

        response_stream = client.completions(messages=messages)

        if stream:
            yield from response_stream.iter_content()
        else:
            response.response_json = {"message": {"content": response_stream.message}}
            yield response.response_json["message"]["content"]

    def build_messages(
        self, prompt: llm.Prompt, conversation: Union[llm.Conversation, None]
    ) -> list[dict[str, str]]:
        messages = []
        if not conversation:
            if prompt.system:
                messages.append(
                    {
                        "role": "system",
                        "content": prompt.system,
                        "message_id": str(uuid4()),
                    }
                )
            messages.append(
                {"role": "user", "content": prompt.prompt, "message_id": str(uuid4())}
            )
            return messages
        current_system = None
        for prev_response in conversation.responses:
            if (
                prev_response.prompt.system
                and prev_response.prompt.system != current_system
            ):
                messages.append(
                    {
                        "role": "system",
                        "content": prev_response.prompt.system,
                        "message_id": str(uuid4()),
                    },
                )
                current_system = prev_response.prompt.system
            messages.append(
                {
                    "role": "user",
                    "content": prev_response.prompt.prompt,
                    "message_id": str(uuid4()),
                }
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": prev_response.text(),
                    "message_id": str(uuid4()),
                }
            )
        if prompt.system and prompt.system != current_system:
            messages.append(
                {"role": "system", "content": prompt.system, "message_id": str(uuid4())}
            )
        messages.append(
            {"role": "user", "content": prompt.prompt, "message_id": str(uuid4())}
        )
        return messages
