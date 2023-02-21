"""
Parse the configuration file `configuration.yaml`.
"""
import dataclasses
import getpass
import json
import os
import pathlib
import sys
from typing import Any, Dict, List, Optional

import yaml

from antareslauncher import __author__, __project_name__, __version__
from antareslauncher.exceptions import (
    InvalidConfigValueError,
    UnknownFileSuffixError,
    ConfigFileNotFoundError,
)

APP_NAME = __project_name__
APP_AUTHOR = __author__.split(",")[0]
APP_VERSION = ".".join(__version__.split(".")[:2])  # "MAJOR.MINOR"

CONFIGURATION_YAML = "configuration.yaml"


def parse_config(config_path: pathlib.Path) -> Dict[str, Any]:
    """
    This function takes a file path, checks its extension, and reads the contents
    of the file as either YAML or JSON and returns it as a dictionary.

    Args:
        config_path: Full path of the configuration file.

    Returns:
        Content of the configuration file as a dictionary.

    Raises:
        `UnknownFileSuffixError`: If the file extension is not '.yaml', '.yml', or '.json'.
    """
    suffix = config_path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        with config_path.open(encoding="utf-8") as fd:
            obj = yaml.load(fd, Loader=yaml.FullLoader)
    elif suffix in {".json"}:
        text = config_path.read_text(encoding="utf-8")
        obj = json.loads(text)
    else:
        raise UnknownFileSuffixError(config_path, config_path.suffix)
    return obj


def dump_config(config_path: pathlib.Path, obj: Dict[str, Any]) -> None:
    """
    This function takes a file path, checks its extension, and write
    the dictionary object in the file as either YAML or JSON.

    Args:
        config_path: Full path of the configuration file.
        obj: Configuration file to write.
    """
    suffix = config_path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        with config_path.open(mode="w", encoding="utf-8") as fd:
            yaml.dump(obj, fd, allow_unicode=True, sort_keys=False, indent=2)
    elif suffix in {".json"}:
        config_path.write_text(
            json.dumps(obj, indent=2, sort_keys=False),
            encoding="utf-8",
        )
    else:
        raise UnknownFileSuffixError(config_path, config_path.suffix)


@dataclasses.dataclass
class SSHConfig:
    """
    Configuration of the SSH access.

    Attributes:
    - config_path: Path to the SSH configuration file.
    - username: SSH username.
    - hostname: Hostname or IP address of the SSH server.
    - port: Port number of the SSH service (defaults to 22).
    - private_key_file: Path to the private key file (defaults to None).
    - key_password: Password to use with the private key file (defaults to an empty string).
    - password: Password to use for classic authentication (defaults to an empty string).
    """

    config_path: pathlib.Path
    username: str
    hostname: str
    port: int = 22
    private_key_file: Optional[pathlib.Path] = None
    key_password: str = ""
    password: str = ""

    @classmethod
    def load_config(cls, ssh_config_path: pathlib.Path) -> "SSHConfig":
        """
        Load the SSH configuration from a file and return it as an `SSHConfig` object.

        Args:
            ssh_config_path: Path to the SSH configuration file.

        Returns:
            An `SSHConfig` object populated with the values from the SSH configuration file.

        The file should contain key-value pairs in either YAML or JSON format.
        The keys are case-insensitive and will be converted to lowercase before being used
        to populate the fields of the `SSHConfig` object.
        The `private_key_file` key (if present) will be converted to a `pathlib.Path` object.

        Raises:
            `UnknownFileSuffixError`: If the file extension is not '.yaml', '.yml', or '.json'.
            `InvalidConfigValueError`: If a value is invalid or missing.
        """
        obj = parse_config(ssh_config_path)
        kwargs = {k.lower(): v for k, v in obj.items()}
        private_key_file = kwargs.pop("private_key_file", None)
        kwargs["private_key_file"] = (
            None if private_key_file is None else pathlib.Path(private_key_file)
        )
        try:
            return cls(config_path=ssh_config_path, **kwargs)
        except TypeError as exc:
            raise InvalidConfigValueError(ssh_config_path, str(exc)) from None

    def save_config(self, ssh_config_path: pathlib.Path) -> None:
        """
        Save the SSH configuration file.

        Args:
            ssh_config_path: Path to the SSH configuration file.

        Raises:
            `UnknownFileSuffixError`: If the file extension is not '.yaml', '.yml', or '.json'.
        """
        obj = dataclasses.asdict(self)
        del obj["config_path"]
        obj = {
            k: v
            for k, v in obj.items()
            if v or k not in {"private_key_file", "key_password", "password"}
        }
        if "private_key_file" in obj:
            obj["private_key_file"] = obj["private_key_file"].as_posix()
        dump_config(ssh_config_path, obj)


@dataclasses.dataclass
class Config:
    """
    Represents the configuration for launching studies on a SLURM server using Antares Launcher.

    Attributes:

    - config_path: Path to the Antares Launcher configuration file.
    - log_dir: Path to the directory where logs will be stored.
    - json_dir: Path to the directory where the JSON database will be stored.
    - studies_in_dir: Path to the directory where studies will be read.
    - finished_dir: Path to the directory where finished studies will be downloaded and placed.
    - default_time_limit: The default time limit (in seconds) for each study simulation job.
    - default_n_cpu: The default number of CPUs to be used by each study simulation job.
    - default_wait_time: The default wait time (in seconds) between study simulation jobs.
    - db_primary_key: A string representing the primary key used in the database.
    - default_ssh_configfile_name: The default name of the SSH configuration file.
    - ssh_config_file_is_required: A flag indicating whether an SSH configuration file is required.
    - slurm_script_path: Path to the SLURM script used to launch studies (a Shell script).
    - remote_solver_versions: A list of strings representing the available Antares Solver
      versions on the remote server.
    - ssh_config: An `SSHConfig` object representing the SSH configuration.
    """

    config_path: pathlib.Path
    log_dir: pathlib.Path
    json_dir: pathlib.Path
    studies_in_dir: pathlib.Path
    finished_dir: pathlib.Path
    default_time_limit: int
    default_n_cpu: int
    default_wait_time: int
    db_primary_key: str
    ssh_config_file_is_required: bool
    slurm_script_path: pathlib.Path
    remote_solver_versions: List[str]

    ssh_config: SSHConfig

    @classmethod
    def load_config(cls, config_path: pathlib.Path) -> "Config":
        """
        Load the Antares Launcher configuration from a file and return it as a `Config` object.

        Args:
            config_path: Path to the Antares Launcher configuration file.

        Returns:
            A `Config` object populated with the values from the Antares Launcher configuration file.

        The file should contain key-value pairs in either YAML or JSON format.
        The keys are case-insensitive and will be converted to lowercase before being used
        to populate the fields of the `Config` object. Paths will be converted to `pathlib.Path` objects.
        The SSH configuration file is specified by the `default_ssh_configfile_name` field
        and will be loaded as an `SSHConfig` object.

        Raises:
            `UnknownFileSuffixError`: If the file extension is not '.yaml', '.yml', or '.json'.
            `InvalidConfigValueError`: If a value is invalid or missing.
        """
        obj = parse_config(config_path)
        kwargs = {k.lower(): v for k, v in obj.items()}
        try:
            kwargs["remote_solver_versions"] = kwargs.pop(
                "antares_versions_on_remote_server"
            )
            # handle paths
            for key in [
                "log_dir",
                "json_dir",
                "studies_in_dir",
                "finished_dir",
                "slurm_script_path",
            ]:
                kwargs[key] = pathlib.Path(kwargs[key])
            ssh_configfile_name = kwargs.pop("default_ssh_configfile_name")
        except KeyError as exc:
            raise InvalidConfigValueError(
                config_path, f"missing parameter '{exc}'"
            ) from None
        # handle SSH configuration
        config_dir = config_path.parent
        ssh_config_path = config_dir.joinpath(ssh_configfile_name)
        kwargs["ssh_config"] = SSHConfig.load_config(ssh_config_path)
        try:
            return cls(config_path=config_path, **kwargs)
        except TypeError as exc:
            raise InvalidConfigValueError(config_path, str(exc)) from None

    def save_config(self, config_path: pathlib.Path) -> None:
        """
        Save the Antares Launcher configuration file.

        Args:
            config_path: Path to the configuration file.

        Raises:
            `UnknownFileSuffixError`: If the file extension is not '.yaml', '.yml', or '.json'.
        """
        obj = dataclasses.asdict(self)
        del obj["config_path"]
        del obj["ssh_config"]
        obj["antares_versions_on_remote_server"] = obj.pop("remote_solver_versions")
        for key in [
            "log_dir",
            "json_dir",
            "studies_in_dir",
            "finished_dir",
            "slurm_script_path",
        ]:
            obj[key] = obj[key].as_posix()
        # fmt: off
        obj["default_ssh_configfile_name"] = ssh_config_name = self.ssh_config.config_path.name
        # fmt: on
        dump_config(config_path, obj)
        config_dir = config_path.parent
        self.ssh_config.save_config(config_dir.joinpath(ssh_config_name))


def get_user_config_dir(system: str = ""):
    """
    Retrieve the user configuration directory based on the system platform.

    - On Windows, it returns the path
      `C:\\Users\\<username>\\AppData\\Local\\<APP_AUTHOR>\\<APP_NAME>\\<APP_VERSION>`.
    - On macOS, it returns `~/Library/Preferences/<APP_NAME>/<APP_VERSION>`.
    - On other platforms, it returns `~/.config/<APP_NAME>/<APP_VERSION>`
      depending on the `XDG_CONFIG_HOME` environment variable if it is set.

    Args:
        system: Platform system, by default the platform is auto-detected.

    Returns:
        The user configuration directory path.
    """
    username = getpass.getuser()
    system = system or sys.platform
    if system == "win32":
        config_dir = pathlib.WindowsPath(
            rf"C:\Users\{username}\AppData\Local\{APP_AUTHOR}"
        )
    elif system == "darwin":
        config_dir = pathlib.PosixPath("~/Library/Preferences").expanduser()
    else:
        path = os.getenv("XDG_CONFIG_HOME", "~/.config")
        config_dir = pathlib.PosixPath(path).expanduser()
    return config_dir.joinpath(APP_NAME, APP_VERSION)


def get_config_path(config_name: str = CONFIGURATION_YAML) -> pathlib.Path:
    env_value = os.environ.get("ANTARES_LAUNCHER_CONFIG_PATH")
    if env_value is not None:
        config_path = pathlib.Path(env_value)
        if config_path.exists():
            return config_path
        raise ConfigFileNotFoundError([config_path.parent], config_path.name)
    possible_dirs = [get_user_config_dir(), pathlib.Path("."), pathlib.Path("./data")]
    for config_dir in possible_dirs:
        config_path = config_dir.joinpath(config_name)
        if config_path.exists():
            return config_path
    raise ConfigFileNotFoundError(possible_dirs, config_name)
