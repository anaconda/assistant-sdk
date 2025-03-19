import json
import os
import re
from textwrap import dedent
from typing import Any
from typing import Generator
from typing import Optional
from typing import List
from typing import Dict
from typing import Union
from uuid import uuid4

from requests import Response
from requests.exceptions import HTTPError

from anaconda_cli_base.config import anaconda_config_path
from anaconda_auth.client import BaseClient as AuthClient
from anaconda_assistant.api_client import APIClient
from anaconda_assistant.exceptions import NotAcceptedTermsError
from anaconda_assistant.exceptions import UnspecifiedAcceptedTermsError
from anaconda_assistant.exceptions import UnspecifiedDataCollectionChoice
from anaconda_assistant.exceptions import DailyQuotaExceeded

TOKEN_COUNT = re.compile(
    r"(?P<message>.*)__TOKENS_(?P<used>[0-9]+)\/(?P<limit>[0-9]+)__", re.DOTALL
)

HERE = os.path.dirname(__file__)


class ChatResponse:
    """Process the API response from ChatClient

    The response currently includes tokens used and
    token limit at the end of the response text. Methods
    here capture this extra metadata and filter it out from
    the response text."""

    def __init__(self, response: Response) -> None:
        self._response = response
        self._message: Optional[str] = None
        self.tokens_used: int = 0
        self.token_limit: int = 0

    @property
    def message_id(self) -> str:
        if self._response.request.body is None:
            raise ValueError("The chat response from the API is malformed.")

        return json.loads(self._response.request.body)["response_message_id"]

    def _match_tokens(self, text: str) -> Dict[str, Any]:
        matched = re.match(TOKEN_COUNT, text)
        if matched is None:
            return {"message": text, "used": None, "limit": None}
        else:
            return matched.groupdict()

    @property
    def message(self) -> str:
        if self._message is None:
            for _ in self.iter_content():
                # first consume the message
                ...
            if self._message is None:
                raise ValueError("Something is wrong with this response")

        return self._message

    def iter_content(
        self, chunk_size: int = 256, decode_unicode: bool = True
    ) -> Generator[str, None, None]:
        message = ""
        for chunk in self._response.iter_content(
            chunk_size=chunk_size, decode_unicode=decode_unicode
        ):
            matched = self._match_tokens(chunk)

            if matched.get("used"):
                self.tokens_used = int(matched["used"])
                self.token_limit = int(matched["limit"])

            message += matched["message"]
            yield matched["message"]

        self._message = message

    def iter_lines(
        self,
        chunk_size: int = 512,
        decode_unicode: bool = True,
        delimiter: Optional[str] = None,
    ) -> Generator[str, None, None]:
        message = ""
        for chunk in self._response.iter_lines(
            chunk_size=chunk_size, decode_unicode=decode_unicode, delimiter=delimiter
        ):
            matched = self._match_tokens(chunk)

            if matched.get("used"):
                self.tokens_used = matched["used"]
                self.token_limit = matched["limit"]

            message += matched["message"]
            yield matched["message"]

        self._message = message


class ChatClient:
    def __init__(
        self,
        system_message: Optional[str] = None,
        example_messages: Optional[List[Dict[str, str]]] = None,
        domain: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
    ) -> None:
        """Anaconda Assistant Client

        This class facilitates requesting completions for a given list of messages"""

        self.api_client: APIClient = APIClient(
            domain=domain, api_key=api_key, api_version=api_version
        )
        self.auth_client: AuthClient = AuthClient(api_key=api_key)

        if self.api_client._config.accepted_terms is None:
            msg = dedent(f"""\
                You have not accepted the terms of service.
                You must accept our terms of service and Privacy Policy
                https://anaconda.com/legal
                If you confirm that you are older than 13 years old and accept the terms
                please set this configuration in {anaconda_config_path()} as follows:

                [plugin.assistant]
                accepted_terms = true
                """)
            raise UnspecifiedAcceptedTermsError(msg)
        elif not self.api_client._config.accepted_terms:
            raise NotAcceptedTermsError(
                f"You have declined our Terms of Service and Privacy Policy in {anaconda_config_path()}"
            )

        if self.api_client._config.data_collection is None:
            msg = dedent(f"""\
                You have not declared to opt-in or opt-out of data collection. Please set this configuration in
                {anaconda_config_path()} as follows to enable data collection:

                [plugin.assistant]
                data_collection = true

                or to disable data collection:

                [plugin.assistant]
                data_collection = false
                """)
            raise UnspecifiedDataCollectionChoice(msg)

        self.id: str = str(uuid4())

        self.system_message = system_message
        self.example_messages = example_messages
        self.skip_logging = not self.api_client._config.data_collection

    def completions(
        self,
        messages: List[Dict[str, str]],
        variables: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """Return completions from the Anaconda Assistant as a ChatResponse type"""

        response_message_id = str(uuid4())

        body = {
            "skip_logging": self.skip_logging,
            "session": {
                "session_id": self.id,
                "user_id": self.auth_client.email,
                "iteration_id": 1,
            },
            "chat_context": {
                "type": "custom-prompt",
                "variables": {} if variables is None else variables,
            },
            "messages": messages,
            "response_message_id": response_message_id,
        }

        if self.system_message:
            body["custom_prompt"] = {
                "system_message": {"role": "system", "content": self.system_message},
                "example_messages": self.example_messages,
            }

        response = self.api_client.post("/completions", json=body, stream=True)
        response.encoding = "utf-8"
        try:
            response.raise_for_status()
        except HTTPError as e:
            try:
                msg = response.json().get("message")
                if msg is None:
                    msg = response.text
            except json.JSONDecodeError:
                msg = response.reason
            e.args = (f"{e.args[0]}. {msg}",)

            if e.response.status_code == 429:
                raise DailyQuotaExceeded(
                    "You have reached your request limit. Please try again in 24 hours.\n"
                    "Or visit https://anaconda.cloud/profile/subscriptions to upgrade your account"
                )

            raise

        cp = ChatResponse(response)
        return cp


class ChatSession:
    """Anaconda Assistant Chat Session

    This Session provides a simple .chat() method that
    takes a single user message and returns (or streams)
    a response. All user messages and assistant responses
    are saved in the .messages stack so you can use the session
    to have a long-running conversation with the Anaconda Assistant.
    """

    def __init__(
        self,
        system_message: Optional[str] = None,
        domain: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
    ) -> None:
        self.client = ChatClient(
            system_message=system_message,
            domain=domain,
            api_key=api_key,
            api_version=api_version,
        )
        self.messages: list = []
        self.usage: dict = {"tokens_used": 0, "token_limit": 0}

    def reset(self) -> None:
        """Reset chat history

        This will remove all input messages and responses and
        create a new chat session id."""

        self.id: str = str(uuid4())
        self.messages = []
        self.usage = {"tokens_used": 0, "token_limit": 0}

    def _stream(self, response: ChatResponse) -> Generator[str, None, None]:
        """Stream and save the response"""
        yield from response.iter_content()
        self.messages.append(
            {
                "role": "assistant",
                "content": response.message,
                "message_id": response.message_id,
            }
        )
        self.usage["tokens_used"] = response.tokens_used
        self.usage["token_limit"] = response.token_limit

    def _text(self, response: ChatResponse) -> str:
        """Save and return the response"""
        self.messages.append(
            {
                "role": "assistant",
                "content": response.message,
                "message_id": response.message_id,
            }
        )
        self.usage["tokens_used"] = response.tokens_used
        self.usage["token_limit"] = response.token_limit
        return response.message

    def chat(
        self, message: str, stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Chat with the Assistant appending your current message to the stack"""
        this_message = {"role": "user", "content": message, "message_id": str(uuid4())}

        messages = self.messages + [this_message]
        response = self.client.completions(messages)

        self.messages.append(this_message)

        if stream:
            return self._stream(response)
        else:
            return self._text(response)
