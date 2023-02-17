import json
import os.path
from pathlib import Path
from typing import Dict, Any

import yaml
import getpass
from antareslauncher.main import MainParameters
from antareslauncher.main_option_parser import ParserParameters

ALT2_PARENT = Path.home() / "antares_launcher_settings"
ALT1_PARENT = Path.cwd()
DEFAULT_JSON_DB_NAME = f"{getpass.getuser()}_antares_launcher_db.json"


class ParametersReader:
    class EmptyFileException(TypeError):
        pass

    class MissingValueException(KeyError):
        pass

    def __init__(self, json_ssh_conf: Path, yaml_filepath: Path):
        self.json_ssh_conf = json_ssh_conf

        with open(Path(yaml_filepath)) as yaml_file:
            self.yaml_content = yaml.load(yaml_file, Loader=yaml.FullLoader) or {}

        self._wait_time = self._get_compulsory_value("DEFAULT_WAIT_TIME")
        self.time_limit = self._get_compulsory_value("DEFAULT_TIME_LIMIT")
        self.n_cpu = self._get_compulsory_value("DEFAULT_N_CPU")
        self.studies_in_dir = os.path.expanduser(self._get_compulsory_value("STUDIES_IN_DIR"))
        self.log_dir = os.path.expanduser(self._get_compulsory_value("LOG_DIR"))
        self.finished_dir = os.path.expanduser(self._get_compulsory_value("FINISHED_DIR"))
        self.ssh_conf_file_is_required = self._get_compulsory_value(
            "SSH_CONFIG_FILE_IS_REQUIRED"
        )

        alt1, alt2 = self._get_ssh_conf_file_alts()
        self.ssh_conf_alt1, self.ssh_conf_alt2 = alt1, alt2
        self.default_ssh_dict = self._get_ssh_dict_from_json()
        self.remote_slurm_script_path = self._get_compulsory_value("SLURM_SCRIPT_PATH")
        self.antares_versions = self._get_compulsory_value(
            "ANTARES_VERSIONS_ON_REMOTE_SERVER"
        )
        self.db_primary_key = self._get_compulsory_value("DB_PRIMARY_KEY")
        self.json_dir = Path(self._get_compulsory_value("JSON_DIR")).expanduser()
        self.json_db_name = self.yaml_content.get(
            "DEFAULT_JSON_DB_NAME", DEFAULT_JSON_DB_NAME
        )

    def get_parser_parameters(self):

        options = ParserParameters(
            default_wait_time=self._wait_time,
            default_time_limit=self.time_limit,
            default_n_cpu=self.n_cpu,
            studies_in_dir=self.studies_in_dir,
            log_dir=self.log_dir,
            finished_dir=self.finished_dir,
            ssh_config_file_is_required=self.ssh_conf_file_is_required,
            ssh_configfile_path_alternate1=self.ssh_conf_alt1,
            ssh_configfile_path_alternate2=self.ssh_conf_alt2,
        )
        return options

    def get_main_parameters(self) -> MainParameters:

        main_parameters = MainParameters(
            json_dir=self.json_dir,
            default_json_db_name=self.json_db_name,
            slurm_script_path=self.remote_slurm_script_path,
            antares_versions_on_remote_server=self.antares_versions,
            default_ssh_dict=self.default_ssh_dict,
            db_primary_key=self.db_primary_key,
        )
        return main_parameters

    def _get_ssh_conf_file_alts(self):
        default_alternate1, default_alternate2 = self._get_default_alternate_values()
        ssh_conf_alternate1 = self.yaml_content.get(
            "SSH_CONFIGFILE_PATH_ALTERNATE1",
            default_alternate1,
        )
        ssh_conf_alternate2 = self.yaml_content.get(
            "SSH_CONFIGFILE_PATH_ALTERNATE2",
            default_alternate2,
        )
        return ssh_conf_alternate1, ssh_conf_alternate2

    def _get_default_alternate_values(self):
        default_ssh_configfile_name = self._get_compulsory_value(
            "DEFAULT_SSH_CONFIGFILE_NAME"
        )
        default_alternate1 = ALT1_PARENT / default_ssh_configfile_name
        default_alternate2 = ALT2_PARENT / default_ssh_configfile_name
        return default_alternate1, default_alternate2

    def _get_compulsory_value(self, key: str):
        try:
            value = self.yaml_content[key]
        except KeyError as e:
            print(f"missing value: {str(e)}")
            raise ParametersReader.MissingValueException(e) from None
        return value

    def _get_ssh_dict_from_json(self) -> Dict[str, Any]:
        with open(self.json_ssh_conf) as ssh_connection_json:
            ssh_dict = json.load(ssh_connection_json)
        if "private_key_file" in ssh_dict:
            ssh_dict["private_key_file"] = os.path.expanduser(ssh_dict["private_key_file"])
        return ssh_dict
