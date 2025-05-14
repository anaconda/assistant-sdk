from pathlib import Path

import tomli
from pytest import MonkeyPatch
from anaconda_assistant_conda.core import set_config
from anaconda_cli_base.config import anaconda_config_path


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
        data = tomli.load(f)
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
        data = tomli.load(f)
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
        data = tomli.load(f)
        assert data["test_table"]["foo"] == "bar"  # type: ignore


def test_set_config_override_anaconda_config_toml(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    config_toml = tmp_path / ".anaconda" / "config.toml"
    config_toml.parent.mkdir(parents=True, exist_ok=True)
    config_toml.write_text('[test_table]\nfoo = "baz"')

    with config_toml.open("rb") as f:
        data = tomli.load(f)
        assert data["test_table"]["foo"] == "baz"  # type: ignore

    monkeypatch.setenv("ANACONDA_CONFIG_TOML", str(config_toml))
    assert anaconda_config_path() == config_toml
    assert anaconda_config_path().exists()

    set_config("test_table", "foo", "bar")

    assert anaconda_config_path().exists()

    with config_toml.open("rb") as f:
        data = tomli.load(f)
        assert data["test_table"]["foo"] == "bar"  # type: ignore
