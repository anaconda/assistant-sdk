from typing import Any
from typing import Generator

import json
import pytest
import responses
from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from requests.exceptions import StreamConsumedError
import responses.matchers

from anaconda_assistant import __version__ as version
from anaconda_assistant.exceptions import (
    DailyQuotaExceeded,
    NotAcceptedTermsError,
    UnspecifiedAcceptedTermsError,
    UnspecifiedDataCollectionChoice,
)
from anaconda_assistant.core import ChatSession, ChatClient
from anaconda_assistant.api_client import APIClient


def test_unspecified_accepted_terms_error() -> None:
    with pytest.raises(UnspecifiedAcceptedTermsError):
        _ = ChatClient()


def test_not_accepted_terms_error(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "false")
    with pytest.raises(NotAcceptedTermsError):
        _ = ChatClient()


def test_unspecified_data_collection(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    with pytest.raises(UnspecifiedDataCollectionChoice):
        _ = ChatClient()


@pytest.fixture
def mocked_api_domain(mocker: MockerFixture) -> Generator[str, None, None]:
    mocker.patch(
        "anaconda_auth.client.BaseClient.email",
        return_value="me@example.com",
        new_callable=mocker.PropertyMock,
    )

    api_client = APIClient(domain="mocking-assistant")

    with responses.RequestsMock(assert_all_requests_are_fired=False) as resp:
        resp.add(
            responses.POST,
            api_client.urljoin("/completions"),
            status=429,
            body=json.dumps({"message": "Too many requests"}),
            match=[
                responses.matchers.json_params_matcher(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": "I've said too much",
                                "message_id": "0",
                            }
                        ]
                    },
                    strict_match=False,
                )
            ],
        )
        resp.add(
            responses.POST,
            api_client.urljoin("/completions"),
            body=(
                "I am Anaconda Assistant, an AI designed to help you with a variety of tasks, "
                "answer questions, and provide information on a wide range of topics. How can "
                "I assist you today?__TOKENS_42/424242__"
            ),
        )
        yield "mocking-assistant"


@pytest.fixture
def mocked_api_client(
    mocked_api_domain: str,
) -> Generator[APIClient, None, None]:
    api_client = APIClient(domain=mocked_api_domain)
    yield api_client


@pytest.fixture
def mocked_chat_client(
    mocked_api_domain: str,
) -> Generator[ChatClient, None, None]:
    client = ChatClient(domain=mocked_api_domain)
    yield client


@pytest.fixture
def mocked_chat_session(
    mocked_api_domain: str,
) -> Generator[ChatSession, None, None]:
    session = ChatSession(domain=mocked_api_domain)
    yield session


def test_chat_client_skip_logging(
    monkeypatch: MonkeyPatch, mocked_api_domain: str
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "false")

    client = ChatClient(domain=mocked_api_domain)
    assert client.skip_logging is True

    messages = [{"role": "user", "content": "Who are you?", "message_id": "0"}]
    res = client.completions(messages=messages)

    assert res._response.request.body is not None
    body = json.loads(res._response.request.body)

    assert body.get("skip_logging") is True


def test_chat_client_no_skip_logging(
    monkeypatch: MonkeyPatch, mocked_api_domain: str
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")

    client = ChatClient(domain=mocked_api_domain)
    assert client.skip_logging is False

    messages = [{"role": "user", "content": "Who are you?", "message_id": "0"}]
    res = client.completions(messages=messages)

    assert res._response.request.body is not None
    body = json.loads(res._response.request.body)

    assert body.get("skip_logging") is False


@pytest.fixture
def accepted_terms_and_data_collection(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")


@pytest.mark.usefixtures("accepted_terms_and_data_collection")
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


@pytest.mark.usefixtures("accepted_terms_and_data_collection")
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


@pytest.mark.usefixtures("accepted_terms_and_data_collection")
def test_chat_client_system_message(mocked_api_client: APIClient) -> None:
    system_message = "You are a kitty"

    client = ChatClient(
        system_message=system_message, domain=mocked_api_client.config.domain
    )

    messages = [{"role": "user", "content": "Who are you?", "message_id": "0"}]
    res = client.completions(messages=messages)

    assert res._response.request.body is not None
    body = json.loads(res._response.request.body)

    assert body.get("custom_prompt", {}).get("system_message", "") == {
        "role": "system",
        "content": system_message,
    }


@pytest.mark.usefixtures("accepted_terms_and_data_collection")
def test_chat_client_client_version(mocked_api_client: APIClient) -> None:
    client = ChatClient(domain=mocked_api_client.config.domain)

    messages = [{"role": "user", "content": "Who are you?", "message_id": "0"}]
    res = client.completions(messages=messages)

    assert res._response.request.headers["X-Client-Version"] == version


@pytest.mark.usefixtures("accepted_terms_and_data_collection")
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


@pytest.mark.usefixtures("accepted_terms_and_data_collection")
def test_chat_client_429(mocked_chat_client: ChatClient) -> None:
    messages = [{"role": "user", "content": "I've said too much", "message_id": "0"}]
    with pytest.raises(DailyQuotaExceeded):
        _ = mocked_chat_client.completions(messages=messages)
