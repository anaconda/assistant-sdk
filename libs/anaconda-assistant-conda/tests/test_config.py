import pytest

from pytest import MonkeyPatch
from anaconda_assistant_conda.config import AssistantCondaConfig
from anaconda_assistant.config import AssistantConfig

# Test `AssistantConfig()` dep env patching


@pytest.mark.usefixtures("mock_anaconda_config_toml")
def test_env_patched_1(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    config = AssistantConfig()
    assert config.accepted_terms == True


@pytest.mark.usefixtures("mock_anaconda_config_toml")
def test_env_patched_2(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "false")
    config = AssistantConfig()
    assert config.accepted_terms == False


# Test `AssistantCondaConfig()` from this package


@pytest.mark.usefixtures("mock_anaconda_config_toml")
def test_conda_assistant_env_default() -> None:
    config = AssistantCondaConfig()
    assert config.debug_error_mode == None


@pytest.mark.usefixtures("mock_anaconda_config_toml")
def test_conda_assistant_env_patched(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_DEBUG_ERROR_MODE", "ask")
    config = AssistantCondaConfig()
    assert config.debug_error_mode == "ask"
