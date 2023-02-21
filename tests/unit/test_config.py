import contextlib
import getpass
import json
import pathlib
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from antareslauncher.config import (
    APP_AUTHOR,
    APP_NAME,
    APP_VERSION,
    CONFIGURATION_YAML,
    Config,
    SSHConfig,
    dump_config,
    get_config_path,
    get_user_config_dir,
    parse_config,
)
from antareslauncher.exceptions import (
    ConfigFileNotFoundError,
    InvalidConfigValueError,
    UnknownFileSuffixError,
)


class TestParseConfig:
    @pytest.mark.parametrize("suffix", [".yaml", ".yml", ".json", ".py"])
    @pytest.mark.parametrize("casing", [None, str.upper, str.title])
    def test_parse_config(self, tmp_path, suffix, casing):
        data = {"key1": "value1", "key2": 56}
        # noinspection PyArgumentList
        new_suffix = suffix if casing is None else casing(suffix)
        config_path = tmp_path.joinpath(f"my_config{new_suffix}")
        if suffix in {".yaml", ".yml"}:
            with config_path.open(mode="w", encoding="utf-8") as fd:
                yaml.dump(data, fd)
            actual = parse_config(config_path)
            assert actual == data
        elif suffix in {".json"}:
            config_path.write_text(json.dumps(data), encoding="utf-8")
            actual = parse_config(config_path)
            assert actual == data
        else:
            config_path.write_text(repr(data), encoding="utf-8")
            with pytest.raises(UnknownFileSuffixError):
                parse_config(config_path)


class TestSaveConfig:
    @pytest.mark.parametrize("suffix", [".yaml", ".yml", ".json", ".py"])
    @pytest.mark.parametrize("casing", [None, str.upper, str.title])
    def test_save_config(self, tmp_path, suffix, casing):
        data = {"key1": "value1", "key2": 56}
        # noinspection PyArgumentList
        new_suffix = suffix if casing is None else casing(suffix)
        config_path = tmp_path.joinpath(f"my_config{new_suffix}")
        if suffix in {".yaml", ".yml"}:
            dump_config(config_path, data)
            with config_path.open(encoding="utf-8") as fd:
                actual = yaml.load(fd, Loader=yaml.FullLoader)
            assert actual == data
        elif suffix in {".json"}:
            dump_config(config_path, data)
            actual = json.loads(config_path.read_text(encoding="utf-8"))
            assert actual == data
        else:
            with pytest.raises(UnknownFileSuffixError):
                dump_config(config_path, data)


class TestSSHConfig:
    def test_load_config__with_private_key_file(self, tmp_path):
        data = {
            "username": "john.doe",
            "hostname": "localhost",
            "port": 22,
            "private_key_file": "path/to/private.key",
            "key_password": "key_password",
        }
        config_path = tmp_path.joinpath("my_ssh_config.json")
        config_path.write_text(json.dumps(data), encoding="utf-8")
        config = SSHConfig.load_config(config_path)
        assert config.config_path == config_path
        assert config.username == data["username"]
        assert config.hostname == data["hostname"]
        assert config.port == data["port"]
        assert config.private_key_file == Path(data["private_key_file"])
        assert config.key_password == data["key_password"]
        assert config.password == ""

    def test_load_config__with_password(self, tmp_path):
        data = {
            "username": "john.doe",
            "hostname": "localhost",
            "port": 22,
            "password": "S3Cr3T",
        }
        config_path = tmp_path.joinpath("my_ssh_config.json")
        config_path.write_text(json.dumps(data), encoding="utf-8")
        config = SSHConfig.load_config(config_path)
        assert config.config_path == config_path
        assert config.username == data["username"]
        assert config.hostname == data["hostname"]
        assert config.port == data["port"]
        assert config.private_key_file is None
        assert config.key_password == ""
        assert config.password == data["password"]

    @pytest.mark.parametrize("required", ["username", "hostname"])
    def test_load_config__missing_parameter(self, tmp_path, required):
        data = {
            "username": "john.doe",
            "hostname": "localhost",
            "port": 22,
            "password": "S3Cr3T",
        }
        del data[required]
        config_path = tmp_path.joinpath("my_ssh_config.json")
        config_path.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(InvalidConfigValueError):
            SSHConfig.load_config(config_path)

    def test_save_config__with_private_key_file(self, tmp_path):
        config_path = tmp_path.joinpath("my_ssh_config.json")
        config = SSHConfig(
            config_path=config_path,
            username="john.doe",
            hostname="localhost",
            port=22,
            private_key_file=pathlib.Path("path/to/private.key"),
            key_password="key_password",
        )
        config.save_config(config_path)
        actual = json.loads(config_path.read_text(encoding="utf-8"))
        assert "config_path" not in actual
        assert actual["username"] == config.username
        assert actual["hostname"] == config.hostname
        assert actual["port"] == config.port
        assert actual["private_key_file"] == config.private_key_file.as_posix()
        assert actual["key_password"] == config.key_password
        assert "password" not in actual

    def test_save_config__with_password(self, tmp_path):
        config_path = tmp_path.joinpath("my_ssh_config.json")
        config = SSHConfig(
            config_path=config_path,
            username="john.doe",
            hostname="localhost",
            port=22,
            password="S3Cr3T",
        )
        config.save_config(config_path)
        actual = json.loads(config_path.read_text(encoding="utf-8"))
        assert "config_path" not in actual
        assert actual["username"] == config.username
        assert actual["hostname"] == config.hostname
        assert actual["port"] == config.port
        assert "private_key_file" not in actual
        assert "key_password" not in actual
        assert actual["password"] == config.password


class TestConfig:
    @pytest.fixture(name="ssh_config_path")
    def fixture_ssh_config_path(self, tmp_path) -> pathlib.Path:
        data = {
            "username": "john.doe",
            "hostname": "localhost",
            "port": 22,
            "password": "S3Cr3T",
        }
        config_path = tmp_path.joinpath("ssh_config.json")
        config_path.write_text(json.dumps(data), encoding="utf-8")
        return config_path

    @pytest.fixture(name="ssh_config")
    def fixture_ssh_config(self, tmp_path) -> SSHConfig:
        config_path = tmp_path.joinpath("ssh_config.json")
        return SSHConfig(
            config_path=config_path,
            username="john.doe",
            hostname="localhost",
            port=22,
            password="S3Cr3T",
        )

    def test_load_config__nominal(self, tmp_path, ssh_config_path):
        log_dir = tmp_path.joinpath("log_dir")
        json_dir = tmp_path.joinpath("json_dir")
        studies_in_dir = tmp_path.joinpath("studies_in_dir")
        finished_dir = tmp_path.joinpath("finished_dir")
        slurm_script_path = tmp_path.joinpath("slurm_script.sh")
        data = {
            "log_dir": str(log_dir),
            "json_dir": str(json_dir),
            "studies_in_dir": str(studies_in_dir),
            "finished_dir": str(finished_dir),
            "default_time_limit": 3600,
            "default_n_cpu": 2,
            "default_wait_time": 60,
            "db_primary_key": "pk",
            "default_ssh_configfile_name": ssh_config_path.name,
            "ssh_config_file_is_required": True,
            "slurm_script_path": str(slurm_script_path),
            "antares_versions_on_remote_server": ["8.4.0", "8.5.0"],
        }
        config_path = tmp_path.joinpath("configuration.yaml")
        with config_path.open(mode="w", encoding="utf-8") as fd:
            yaml.dump(data, fd)
        config = Config.load_config(config_path)
        assert config.config_path == config_path
        assert config.log_dir == log_dir
        assert config.json_dir == json_dir
        assert config.studies_in_dir == studies_in_dir
        assert config.finished_dir == finished_dir
        assert config.default_time_limit == data["default_time_limit"]
        assert config.default_n_cpu == data["default_n_cpu"]
        assert config.default_wait_time == data["default_wait_time"]
        assert config.db_primary_key == data["db_primary_key"]
        assert config.ssh_config_file_is_required == data["ssh_config_file_is_required"]
        assert config.slurm_script_path == slurm_script_path
        assert (
            config.remote_solver_versions == data["antares_versions_on_remote_server"]
        )

    def test_save_config__nominal(self, tmp_path, ssh_config):
        config_path = tmp_path.joinpath("configuration.yaml")
        log_dir = tmp_path.joinpath("log_dir")
        json_dir = tmp_path.joinpath("json_dir")
        studies_in_dir = tmp_path.joinpath("studies_in_dir")
        finished_dir = tmp_path.joinpath("finished_dir")
        slurm_script_path = tmp_path.joinpath("slurm_script.sh")
        config = Config(
            config_path=config_path,
            log_dir=log_dir,
            json_dir=json_dir,
            studies_in_dir=studies_in_dir,
            finished_dir=finished_dir,
            default_time_limit=3600,
            default_n_cpu=2,
            default_wait_time=60,
            db_primary_key="pk",
            ssh_config_file_is_required=True,
            slurm_script_path=slurm_script_path,
            remote_solver_versions=["8.4.0", "8.5.0"],
            ssh_config=ssh_config,
        )
        config.save_config(config_path)
        with config_path.open(encoding="utf-8") as fd:
            actual = yaml.load(fd, Loader=yaml.FullLoader)

        assert "config_path" not in actual
        assert actual["log_dir"] == log_dir.as_posix()
        assert actual["json_dir"] == json_dir.as_posix()
        assert actual["studies_in_dir"] == studies_in_dir.as_posix()
        assert actual["finished_dir"] == finished_dir.as_posix()
        assert actual["default_time_limit"] == config.default_time_limit
        assert actual["default_n_cpu"] == config.default_n_cpu
        assert actual["default_wait_time"] == config.default_wait_time
        assert actual["db_primary_key"] == config.db_primary_key
        assert (
            actual["ssh_config_file_is_required"] == config.ssh_config_file_is_required
        )
        assert actual["slurm_script_path"] == slurm_script_path.as_posix()
        assert (
            actual["antares_versions_on_remote_server"] == config.remote_solver_versions
        )
        assert "ssh_config" not in actual

    @pytest.mark.parametrize(
        "required",
        [
            "log_dir",
            "json_dir",
            "studies_in_dir",
            "finished_dir",
            "default_time_limit",
            "default_n_cpu",
            "default_wait_time",
            "db_primary_key",
            "default_ssh_configfile_name",
            "ssh_config_file_is_required",
            "slurm_script_path",
            "antares_versions_on_remote_server",
        ],
    )
    def test_load_config__missing_parameter(self, tmp_path, ssh_config_path, required):
        log_dir = tmp_path.joinpath("log_dir")
        json_dir = tmp_path.joinpath("json_dir")
        studies_in_dir = tmp_path.joinpath("studies_in_dir")
        finished_dir = tmp_path.joinpath("finished_dir")
        slurm_script_path = tmp_path.joinpath("slurm_script.sh")
        data = {
            "log_dir": str(log_dir),
            "json_dir": str(json_dir),
            "studies_in_dir": str(studies_in_dir),
            "finished_dir": str(finished_dir),
            "default_time_limit": 3600,
            "default_n_cpu": 2,
            "default_wait_time": 60,
            "db_primary_key": "pk",
            "default_ssh_configfile_name": ssh_config_path.name,
            "ssh_config_file_is_required": True,
            "slurm_script_path": str(slurm_script_path),
            "antares_versions_on_remote_server": ["8.4.0", "8.5.0"],
        }
        del data[required]
        config_path = tmp_path.joinpath("configuration.yaml")
        with config_path.open(mode="w", encoding="utf-8") as fd:
            yaml.dump(data, fd)
        with pytest.raises(InvalidConfigValueError):
            Config.load_config(config_path)


class TestGetUserConfigDir:
    @pytest.mark.parametrize(
        "system, expected",
        [
            (
                "win32",
                r"C:\Users\{username}\AppData\Local\{APP_AUTHOR}\{APP_NAME}\{APP_VERSION}",
            ),
            (
                "darwin",
                "~/Library/Preferences/{APP_NAME}/{APP_VERSION}",
            ),
            (
                "linux2",
                "~/.config/{APP_NAME}/{APP_VERSION}",
            ),
        ],
    )
    def test_get_user_config_dir(self, system, expected, monkeypatch):
        # ignore error `XDG_CONFIG_HOME` environment variable
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        # ignore error: "cannot instantiate 'WindowsPath'/'PosixPath' on your system"
        with contextlib.suppress(NotImplementedError):
            actual = get_user_config_dir(system)
            expected = expected.format(
                username=getpass.getuser(),
                APP_AUTHOR=APP_AUTHOR,
                APP_NAME=APP_NAME,
                APP_VERSION=APP_VERSION,
            )
            expected = Path(expected).expanduser()
            assert actual == expected


class TestGetConfigPath:
    def test_get_config_path__from_env(self, monkeypatch, tmp_path):
        config_path = tmp_path.joinpath("my_config.yaml")
        config_path.touch()
        monkeypatch.setenv("ANTARES_LAUNCHER_CONFIG_PATH", str(config_path))
        actual = get_config_path()
        assert actual == config_path

    def test_get_config_path__from_env__not_found(self, monkeypatch, tmp_path):
        config_path = tmp_path.joinpath("my_config.yaml")
        monkeypatch.setenv("ANTARES_LAUNCHER_CONFIG_PATH", str(config_path))
        with pytest.raises(ConfigFileNotFoundError):
            get_config_path()

    @pytest.mark.parametrize("config_name", [None, CONFIGURATION_YAML, "my_config.yaml"])
    def test_get_config_path__from_user_config_dir(
        self, monkeypatch, tmp_path, config_name
    ):
        config_path = tmp_path.joinpath(config_name or CONFIGURATION_YAML)
        config_path.touch()
        monkeypatch.delenv("ANTARES_LAUNCHER_CONFIG_PATH", raising=False)
        # noinspection SpellCheckingInspection
        with patch("antareslauncher.config.get_user_config_dir", new=lambda: tmp_path):
            args = (config_name,) if config_name else ()
            actual = get_config_path(*args)
        assert actual == config_path

    @pytest.mark.parametrize("relpath", ["", "data"])
    @pytest.mark.parametrize("config_name", [None, CONFIGURATION_YAML, "my_config.yaml"])
    def test_get_config_path__from_curr_dir(self, monkeypatch, tmp_path, relpath, config_name):
        data_dir = tmp_path.joinpath(relpath)
        data_dir.mkdir(exist_ok=True)
        config_path: pathlib.Path = tmp_path.joinpath(data_dir, config_name or CONFIGURATION_YAML)
        config_path.touch()
        monkeypatch.delenv("ANTARES_LAUNCHER_CONFIG_PATH", raising=False)
        monkeypatch.chdir(tmp_path)
        args = (config_name,) if config_name else ()
        actual = get_config_path(*args)
        assert actual == config_path.relative_to(tmp_path)

    @pytest.mark.parametrize("relpath", ["", "data"])
    def test_get_config_path__from_curr_dir__not_found(
        self, monkeypatch, tmp_path, relpath
    ):
        data_dir = tmp_path.joinpath(relpath)
        data_dir.mkdir(exist_ok=True)
        monkeypatch.delenv("ANTARES_LAUNCHER_CONFIG_PATH", raising=False)
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ConfigFileNotFoundError):
            get_config_path()
