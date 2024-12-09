from typing import Any
from typing import Generator

import json
import pytest
import responses
from pytest_mock import MockerFixture
from requests.exceptions import StreamConsumedError

from anaconda_assistant.core import ChatSession, ChatClient
from anaconda_assistant.api_client import APIClient


@pytest.fixture
def mocked_api_client(mocker: MockerFixture) -> Generator[APIClient, None, None]:
    mocker.patch(
        "anaconda_cloud_auth.client.BaseClient.email",
        return_value="me@example.com",
        new_callable=mocker.PropertyMock,
    )

    api_client = APIClient(domain="mocking-assistant")

    with responses.RequestsMock() as resp:
        resp.add(
            responses.POST,
            api_client.urljoin("/completions"),
            body=(
                "I am Anaconda Assistant, an AI designed to help you with a variety of tasks, "
                "answer questions, and provide information on a wide range of topics. How can "
                "I assist you today?__TOKENS_42/424242__"
            ),
        )
        yield api_client


@pytest.fixture
def mocked_chat_client(
    mocked_api_client: APIClient,
) -> Generator[ChatClient, None, None]:
    client = ChatClient(domain=mocked_api_client._config.domain)
    yield client


@pytest.fixture
def mocked_chat_session(
    mocked_api_client: APIClient,
) -> Generator[ChatSession, None, None]:
    session = ChatSession(domain=mocked_api_client._config.domain)
    yield session


def test_token_regex(mocked_chat_client: ChatClient) -> None:
    messages = [{"role": "user", "content": "Who are you?", "message_id": "0"}]
    res = mocked_chat_client.completions(messages=messages)

    assert res.message == (
        "I am Anaconda Assistant, an AI designed to help you with a variety of tasks, "
        "answer questions, and provide information on a wide range of topics. How can "
        "I assist you today?"
    )
    assert res.tokens_used == 42
    assert res.token_limit == 424242


def test_consume_stream_cached_message(mocked_chat_client: ChatClient) -> None:
    messages = [{"role": "user", "content": "Who are you?", "message_id": "0"}]
    res = mocked_chat_client.completions(messages=messages)

    for _ in res.iter_content():
        pass

    with pytest.raises(StreamConsumedError):
        next(res.iter_content())

    assert res.message == (
        "I am Anaconda Assistant, an AI designed to help you with a variety of tasks, "
        "answer questions, and provide information on a wide range of topics. How can "
        "I assist you today?"
    )
    assert res.tokens_used == 42
    assert res.token_limit == 424242


def test_chat_client_system_message(mocked_api_client: APIClient) -> None:
    system_message = "You are a kitty"

    client = ChatClient(
        system_message=system_message, domain=mocked_api_client._config.domain
    )

    messages = [{"role": "user", "content": "Who are you?", "message_id": "0"}]
    res = client.completions(messages=messages)

    assert res._response.request.body is not None
    body = json.loads(res._response.request.body)

    assert body.get("custom_prompt", {}).get("system_message", "") == {
        "role": "system",
        "content": system_message,
    }


def test_chat_session_history(
    mocked_chat_session: ChatSession, is_not_none: Any
) -> None:
    assert mocked_chat_session.messages == []

    _ = mocked_chat_session.chat("Who are you?")

    assert mocked_chat_session.messages == [
        {"role": "user", "content": "Who are you?", "message_id": is_not_none},
        {"role": "assistant", "content": is_not_none, "message_id": is_not_none},
    ]

    _ = mocked_chat_session.chat("What do you want?")

    assert mocked_chat_session.messages == [
        {"role": "user", "content": "Who are you?", "message_id": is_not_none},
        {"role": "assistant", "content": is_not_none, "message_id": is_not_none},
        {"role": "user", "content": "What do you want?", "message_id": is_not_none},
        {"role": "assistant", "content": is_not_none, "message_id": is_not_none},
    ]

    mocked_chat_session.reset()
    assert mocked_chat_session.messages == []
