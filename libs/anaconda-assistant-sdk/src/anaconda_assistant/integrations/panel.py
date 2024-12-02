import os
from typing import Any
from typing import Generator

from anaconda_assistant.core import ChatSession

HERE = os.path.dirname(__file__)


class AnacondaAssistantCallbackHandler:
    def __init__(
        self,
        session: ChatSession,
    ) -> None:
        self.session = session
        self.assistant_avatar = os.path.join(HERE, "Anaconda_Logo.png")
        self.assistant_name = "Anaconda Assistant"

    def __call__(self, content: str, *_: Any) -> Generator[Any, None, None]:
        full_text = ""
        for chunk in self.session.chat(content, stream=True):
            full_text += chunk
            yield {
                "user": self.assistant_name,
                "avatar": self.assistant_avatar,
                "object": full_text,
            }
