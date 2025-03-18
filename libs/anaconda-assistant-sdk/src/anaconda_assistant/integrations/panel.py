import os
from asyncio import sleep
from typing import Any, Optional
from typing import AsyncGenerator

from anaconda_assistant.core import ChatSession

HERE = os.path.dirname(__file__)


class AnacondaAssistantCallbackHandler:
    def __init__(self, session: Optional[ChatSession] = None) -> None:
        if session is None:
            self.session = ChatSession()
        else:
            self.session = session
        self.assistant_avatar = os.path.join(HERE, "Anaconda_Logo.png")
        self.assistant_name = "Anaconda Assistant"

    async def __call__(self, contents: str, *_: Any) -> AsyncGenerator[dict, None]:
        await sleep(0.1)
        full_text = ""
        for chunk in self.session.chat(contents, stream=True):
            full_text += chunk
            yield {
                "user": self.assistant_name,
                "avatar": self.assistant_avatar,
                "object": full_text,
            }
