import getpass
import json
import os.path
import typing as t
from pathlib import Path

import yaml

from antareslauncher.main import MainParameters
from antareslauncher.main_option_parser import ParserParameters
from antares.study.version import SolverMinorVersion

ALT2_PARENT = Path.home() / "antares_launcher_settings"
ALT1_PARENT = Path.cwd()
DEFAULT_JSON_DB_NAME = f"{getpass.getuser()}_antares_launcher_db.json"


class MissingValueException(Exception):
    def __init__(self, yaml_filepath: Path, key: str) -> None:
        super().__init__(f"Missing key '{key}' in '{yaml_filepath}'")


class ParametersReader:
    def __init__(self, json_ssh_conf: Path, yaml_filepath: Path):
        self.json_ssh_conf = json_ssh_conf

        with open(yaml_filepath) as yaml_file:
            obj = yaml.load(yaml_file, Loader=yaml.FullLoader) or {}

        try:
            self.default_wait_time = obj["DEFAULT_WAIT_TIME"]
            self.time_limit = obj["DEFAULT_TIME_LIMIT"]
            self.n_cpu = obj["DEFAULT_N_CPU"]
            self.studies_in_dir = os.path.expanduser(obj["STUDIES_IN_DIR"])
            self.log_dir = os.path.expanduser(obj["LOG_DIR"])
            self.finished_dir = os.path.expanduser(obj["FINISHED_DIR"])
            self.ssh_conf_file_is_required = obj["SSH_CONFIG_FILE_IS_REQUIRED"]
            default_ssh_configfile_name = obj["DEFAULT_SSH_CONFIGFILE_NAME"]
        except KeyError as e:
            raise MissingValueException(yaml_filepath, str(e)) from None

        default_alternate1 = ALT1_PARENT / default_ssh_configfile_name
        default_alternate2 = ALT2_PARENT / default_ssh_configfile_name

        alt1 = obj.get("SSH_CONFIGFILE_PATH_ALTERNATE1", default_alternate1)
        alt2 = obj.get("SSH_CONFIGFILE_PATH_ALTERNATE2", default_alternate2)

        try:
            self.ssh_conf_alt1 = alt1
            self.ssh_conf_alt2 = alt2
            self.default_ssh_dict = self._get_ssh_dict_from_json()
            self.remote_slurm_script_path = obj["SLURM_SCRIPT_PATH"]
            self.partition = obj.get("PARTITION", "")
            self.quality_of_service = obj.get("QUALITY_OF_SERVICE", "")
            self.antares_versions = [SolverMinorVersion.parse(v) for v in obj["ANTARES_VERSIONS_ON_REMOTE_SERVER"]]
            self.db_primary_key = obj["DB_PRIMARY_KEY"]
            self.json_dir = Path(obj["JSON_DIR"]).expanduser()
            self.json_db_name = obj.get("DEFAULT_JSON_DB_NAME", DEFAULT_JSON_DB_NAME)
        except KeyError as e:
            raise MissingValueException(yaml_filepath, str(e)) from None

    def get_parser_parameters(self):
        return ParserParameters(
            default_wait_time=self.default_wait_time,
            default_time_limit=self.time_limit,
            default_n_cpu=self.n_cpu,
            studies_in_dir=self.studies_in_dir,
            log_dir=self.log_dir,
            finished_dir=self.finished_dir,
            ssh_config_file_is_required=self.ssh_conf_file_is_required,
            ssh_configfile_path_alternate1=self.ssh_conf_alt1,
            ssh_configfile_path_alternate2=self.ssh_conf_alt2,
        )

    def get_main_parameters(self) -> MainParameters:
        return MainParameters(
            json_dir=self.json_dir,
            default_json_db_name=self.json_db_name,
            slurm_script_path=self.remote_slurm_script_path,
            partition=self.partition,
            quality_of_service=self.quality_of_service,
            antares_versions_on_remote_server=self.antares_versions,
            default_ssh_dict=self.default_ssh_dict,
            db_primary_key=self.db_primary_key,
        )

    def _get_ssh_dict_from_json(self) -> t.Dict[str, t.Any]:
        with open(self.json_ssh_conf) as ssh_connection_json:
            ssh_dict = json.load(ssh_connection_json)
        if "private_key_file" in ssh_dict:
            ssh_dict["private_key_file"] = os.path.expanduser(ssh_dict["private_key_file"])
        return ssh_dict
