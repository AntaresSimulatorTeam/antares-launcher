"""
Antares Launcher Exceptions
"""
import pathlib
from typing import Sequence


class AntaresLauncherException(Exception):
    """The base-class of all Antares Launcher exceptions."""


class ConfigFileNotFoundError(AntaresLauncherException):
    """Configuration file not found."""

    def __init__(
        self, possible_dirs: Sequence[pathlib.Path], config_name: str, *args
    ) -> None:
        super().__init__(possible_dirs, config_name, *args)

    @property
    def possible_dirs(self) -> Sequence[pathlib.Path]:
        return self.args[0]

    @property
    def config_name(self) -> str:
        return self.args[1]

    def __str__(self):
        possible_dirs = ", ".join(f"'{p}'" for p in self.possible_dirs)
        config_name = self.config_name
        return f"Configuration file '{config_name}' not found in the following locations: {possible_dirs}"


class ConfigError(AntaresLauncherException):
    """A problem with a config file, or a value in one."""

    def __init__(self, config_path: pathlib.Path, *args):
        super().__init__(config_path, *args)

    @property
    def config_path(self) -> pathlib.Path:
        return self.args[0]

    def __str__(self):
        config_path = self.config_path
        return f"Invalid configuration file '{config_path}'"


class UnknownFileSuffixError(ConfigError):
    def __init__(self, config_path: pathlib.Path, suffix: str):
        super().__init__(config_path, suffix)

    @property
    def suffix(self) -> str:
        return self.args[1]

    def __str__(self):
        parent_msg = super().__str__()
        suffix = self.suffix
        return f"{parent_msg}: unknown file suffix '{suffix}'"


class InvalidConfigValueError(ConfigError):
    def __init__(self, config_path: pathlib.Path, error_msg: str):
        super().__init__(config_path, error_msg)

    @property
    def error_msg(self) -> str:
        return self.args[1]

    def __str__(self):
        parent_msg = super().__str__()
        error_msg = self.error_msg
        return f"{parent_msg}: Invalid config value: {error_msg}"
