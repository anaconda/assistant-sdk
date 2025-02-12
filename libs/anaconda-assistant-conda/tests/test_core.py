from pathlib import Path
from typing import cast

import tomlkit
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from anaconda_assistant_conda.core import set_config, stream_response
from anaconda_cli_base.config import anaconda_config_path
from anaconda_assistant_conda.config import AssistantCondaConfig


def test_set_config_missing_anaconda_directory(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    config_toml = tmp_path / ".anaconda" / "config.toml"

    monkeypatch.setenv("ANACONDA_CONFIG_TOML", str(config_toml))
    assert anaconda_config_path() == config_toml
    assert not anaconda_config_path().exists()

    set_config("test_table", "foo", "bar")

    assert anaconda_config_path().exists()

    with config_toml.open("rb") as f:
        data = tomlkit.load(f)
        assert data["test_table"]["foo"] == "bar"  # type: ignore


def test_set_config_missing_anaconda_config_toml(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    config_toml = tmp_path / ".anaconda" / "config.toml"
    config_toml.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("ANACONDA_CONFIG_TOML", str(config_toml))
    assert anaconda_config_path() == config_toml
    assert not anaconda_config_path().exists()

    set_config("test_table", "foo", "bar")

    assert anaconda_config_path().exists()

    with config_toml.open("rb") as f:
        data = tomlkit.load(f)
        assert data["test_table"]["foo"] == "bar"  # type: ignore


def test_set_config_empty_anaconda_config_toml(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    config_toml = tmp_path / ".anaconda" / "config.toml"
    config_toml.parent.mkdir(parents=True, exist_ok=True)
    config_toml.touch()

    monkeypatch.setenv("ANACONDA_CONFIG_TOML", str(config_toml))
    assert anaconda_config_path() == config_toml
    assert anaconda_config_path().exists()

    set_config("test_table", "foo", "bar")

    assert anaconda_config_path().exists()

    with config_toml.open("rb") as f:
        data = tomlkit.load(f)
        assert data["test_table"]["foo"] == "bar"  # type: ignore


def test_set_config_override_anaconda_config_toml(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    config_toml = tmp_path / ".anaconda" / "config.toml"
    config_toml.parent.mkdir(parents=True, exist_ok=True)
    config_toml.write_text('[test_table]\nfoo = "baz"')

    with config_toml.open("rb") as f:
        data = tomlkit.load(f)
        assert data["test_table"]["foo"] == "baz"  # type: ignore

    monkeypatch.setenv("ANACONDA_CONFIG_TOML", str(config_toml))
    assert anaconda_config_path() == config_toml
    assert anaconda_config_path().exists()

    set_config("test_table", "foo", "bar")

    assert anaconda_config_path().exists()

    with config_toml.open("rb") as f:
        data = tomlkit.load(f)
        assert data["test_table"]["foo"] == "bar"  # type: ignore


def test_combine_system_prompt(
    monkeypatch: MonkeyPatch, mocker: MockerFixture, mocked_assistant_domain: str
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_API_KEY", "api-key")

    config = AssistantCondaConfig()
    config.llm.combine_messages = True

    import langchain_core.language_models

    chat = mocker.spy(langchain_core.language_models.BaseChatModel, "stream")

    stream_response(
        llm=config.llm,
        system_message="Please help",
        prompt="Who are you?",
    )

    assert chat.call_args.kwargs.get("input", []) == [
        {"role": "user", "content": "Please help\nWho are you?"}
    ]


def test_separate_system_prompt(
    monkeypatch: MonkeyPatch, mocker: MockerFixture, mocked_assistant_domain: str
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_API_KEY", "api-key")

    config = AssistantCondaConfig()
    config.llm.combine_messages = False

    import langchain_core.language_models

    chat = mocker.spy(langchain_core.language_models.BaseChatModel, "stream")

    stream_response(
        llm=config.llm,
        system_message="Please help",
        prompt="Who are you?",
    )

    assert chat.call_args.kwargs.get("input", []) == [
        {"role": "system", "content": "Please help"},
        {"role": "user", "content": "Who are you?"},
    ]


def test_load_custom_llm_with_params() -> None:
    driver = "langchain_core.language_models.fake_chat_models:GenericFakeChatModel"
    messages = [{"role": "user", "content": "Who are you?"}]

    config = AssistantCondaConfig(
        llm={  # type: ignore
            "driver": driver,
            "combine_messages": False,
            "params": {"messages": iter(messages)},
        }
    )

    llm = cast(GenericFakeChatModel, config.llm.load())

    assert not config.llm.is_default_llm
    assert isinstance(llm, GenericFakeChatModel)
    assert list(llm.messages) == messages
