"""
Antares Launcher Exceptions
"""

import pathlib

from typing import Sequence

from typing_extensions import override


class AntaresLauncherException(Exception):
    """The base-class of all Antares Launcher exceptions."""


class ConfigFileNotFoundError(AntaresLauncherException):
    """Configuration file not found."""

    def __init__(self, possible_dirs: Sequence[pathlib.Path], config_name: str, *args) -> None:
        super().__init__(possible_dirs, config_name, *args)

    @override
    def __str__(self) -> str:
        possible_dirs = ", ".join(f"'{p}'" for p in self.args[0])
        return f"Configuration file '{self.args[1]}' not found in the following locations: {possible_dirs}"


class ConfigError(AntaresLauncherException):
    """A problem with a config file, or a value in one."""

    def __init__(self, config_path: pathlib.Path, *args):
        super().__init__(config_path, *args)

    @override
    def __str__(self) -> str:
        return f"Invalid configuration file '{self.args[0]}'"


class UnknownFileSuffixError(ConfigError):
    def __init__(self, config_path: pathlib.Path, suffix: str):
        super().__init__(config_path, suffix)

    @override
    def __str__(self):
        parent_msg = super().__str__()
        return f"{parent_msg}: unknown file suffix '{self.args[1]}'"


class InvalidConfigValueError(ConfigError):
    def __init__(self, config_path: pathlib.Path, error_msg: str):
        super().__init__(config_path, error_msg)

    @override
    def __str__(self):
        parent_msg = super().__str__()
        return f"{parent_msg}: Invalid config value: {self.args[1]}"
