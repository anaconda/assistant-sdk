from typing import Generator

from anaconda_assistant.core import ChatSession


def test_completions_text_response() -> None:
    session = ChatSession()
    result = session.chat("who are you?")
    assert isinstance(result, str)


def test_completions_stream_response() -> None:
    session = ChatSession()
    result = session.chat("who are you?", stream=True)
    assert isinstance(result, Generator)

    gathered = "".join(result)
    assert isinstance(gathered, str)


def test_cached_messages() -> None:
    session = ChatSession()
    phrase = session.chat("create a random two word phrase")
    reversed_phrase = session.chat("reverse the first and second words")

    assert len(session.messages) == 4
    assert [m["role"] for m in session.messages] == ["user", "assistant"] * 2

    assert reversed_phrase == " ".join(reversed(phrase.split()))


def test_cached_messages_stream() -> None:
    session = ChatSession()
    result = session.chat("create a random two word phrase", stream=True)
    phrase = "".join(result)

    result = session.chat("reverse the first and second words")
    reversed_phrase = "".join(result)

    assert len(session.messages) == 4
    assert [m["role"] for m in session.messages] == ["user", "assistant"] * 2

    assert reversed_phrase == " ".join(reversed(phrase.split()))
