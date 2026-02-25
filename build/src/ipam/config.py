import configparser
import os
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".ipam" / "config"
SECTION_PREFIX = "profile "


def _read_config(config_file: Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    config.read(config_file)
    return config


def _section_name(profile_name: str) -> str:
    return f"{SECTION_PREFIX}{profile_name}"


def _profile_name(section: str) -> str:
    return section.removeprefix(SECTION_PREFIX)


def load_profile(
    name: str, config_file: Path = DEFAULT_CONFIG_PATH
) -> dict[str, str]:
    config = _read_config(config_file)
    section = _section_name(name)
    if not config.has_section(section):
        raise KeyError(f"Profile not found: {name}")
    return dict(config[section])


def save_profile(
    name: str,
    settings: dict[str, str],
    config_file: Path = DEFAULT_CONFIG_PATH,
) -> None:
    config_file.parent.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    if config_file.exists():
        config.read(config_file)

    section = _section_name(name)
    if config.has_section(section):
        config.remove_section(section)
    config.add_section(section)
    for key, value in settings.items():
        config.set(section, key, value)

    with open(config_file, "w") as f:
        config.write(f)

    os.chmod(config_file, 0o600)


def list_profiles(config_file: Path = DEFAULT_CONFIG_PATH) -> list[str]:
    if not config_file.exists():
        return []
    config = configparser.ConfigParser()
    config.read(config_file)
    return [
        _profile_name(s) for s in config.sections() if s.startswith(SECTION_PREFIX)
    ]


def delete_profile(
    name: str, config_file: Path = DEFAULT_CONFIG_PATH
) -> None:
    config = _read_config(config_file)
    section = _section_name(name)
    if not config.has_section(section):
        raise KeyError(f"Profile not found: {name}")
    config.remove_section(section)
    with open(config_file, "w") as f:
        config.write(f)
