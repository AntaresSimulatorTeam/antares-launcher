import getpass
import json
from pathlib import Path

import pytest

from antareslauncher.parameters_reader import ParametersReader


class TestParametersReader:
    def setup_method(self):
        self.SLURM_SCRIPT_PATH = "/path/to/launchAntares_v1.1.3.sh"
        self.SSH_CONFIG_FILE_IS_REQUIRED = False
        self.DEFAULT_SSH_CONFIGFILE_NAME = "ssh_config.json"
        self.DB_PRIMARY_KEY = "name"
        self.DEFAULT_WAIT_TIME = 900
        self.DEFAULT_N_CPU = 12
        self.DEFAULT_TIME_LIMIT = 172800
        self.FINISHED_DIR = "FINISHED"
        self.STUDIES_IN_DIR = "STUDIES-IN"
        self.LOG_DIR = "LOGS"
        self.JSON_DIR = "JSON"
        self.ANTARES_SUPPORTED_VERSIONS = ["610", "700"]

        self.yaml_compulsory_content = (
            f'LOG_DIR : "{self.LOG_DIR}"\n'
            f'JSON_DIR : "{self.JSON_DIR}"\n'
            f'STUDIES_IN_DIR : "{self.STUDIES_IN_DIR}"\n'
            f'FINISHED_DIR : "{self.FINISHED_DIR}"\n'
            f"DEFAULT_TIME_LIMIT : {self.DEFAULT_TIME_LIMIT}\n"
            f"DEFAULT_N_CPU : {self.DEFAULT_N_CPU}\n"
            f"DEFAULT_WAIT_TIME : {self.DEFAULT_WAIT_TIME}\n"
            f'DB_PRIMARY_KEY : "{self.DB_PRIMARY_KEY}"\n'
            f'DEFAULT_SSH_CONFIGFILE_NAME: "{self.DEFAULT_SSH_CONFIGFILE_NAME}"\n'
            f"SSH_CONFIG_FILE_IS_REQUIRED : {self.SSH_CONFIG_FILE_IS_REQUIRED}\n"
            f'SLURM_SCRIPT_PATH : "{self.SLURM_SCRIPT_PATH}"\n'
            f"ANTARES_VERSIONS_ON_REMOTE_SERVER :\n"
            f'  - "{self.ANTARES_SUPPORTED_VERSIONS[0]}"\n'
            f'  - "{self.ANTARES_SUPPORTED_VERSIONS[1]}"\n'
        )
        self.DEFAULT_JSON_DB_NAME = "db_file.json"
        self.yaml_opt_content = (
            f'DEFAULT_JSON_DB_NAME : "{self.DEFAULT_JSON_DB_NAME}\n'
            f'DEFAULT_SSH_CONFIGFILE_NAME: "{self.DEFAULT_SSH_CONFIGFILE_NAME}"\n'
        )
        self.USER = "user"
        self.HOST = "host"
        self.KEY = "C:\\home\\hello"
        self.KEY_PSWD = "hello"
        self.json_dict = {
            "username": self.USER,
            "hostname": self.HOST,
            "private_key_file": self.KEY,
            "key_password": self.KEY_PSWD,
        }

    @pytest.mark.unit_test
    def test_ParametersReader_raises_exception_with_no_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ParametersReader(Path(tmp_path), Path("empty.yaml"))

    @pytest.mark.unit_test
    def test_get_option_parameters_raises_exception_with_empty_file(self, tmp_path):
        empty_json = tmp_path / "dummy.json"
        empty_yaml = tmp_path / "empty.yaml"
        empty_yaml.write_text("")
        with pytest.raises(ParametersReader.MissingValueException):
            ParametersReader(empty_json, empty_yaml).get_parser_parameters()

    @pytest.mark.unit_test
    def test_get_main_parameters_raises_exception_with_empty_file(self, tmp_path):
        empty_json = tmp_path / "dummy.json"
        empty_yaml = tmp_path / "empty.yaml"
        empty_yaml.write_text("")
        with pytest.raises(ParametersReader.MissingValueException):
            ParametersReader(empty_json, empty_yaml).get_main_parameters()

    @pytest.mark.unit_test
    def test_get_option_parameters_raises_exception_if_params_are_missing(
        self, tmp_path
    ):
        empty_json = tmp_path / "dummy.json"
        config_yaml = tmp_path / "empty.yaml"
        config_yaml.write_text(
            'LOG_DIR : "LOGS"\n'
            'JSON_DIR : "JSON"\n'
            'STUDIES_IN_DIR : "STUDIES-IN"\n'
            'FINISHED_DIR : "FINISHED"\n'
            "DEFAULT_TIME_LIMIT : 172800\n"
            "DEFAULT_N_CPU : 2\n"
        )
        with pytest.raises(ParametersReader.MissingValueException):
            ParametersReader(empty_json, config_yaml).get_parser_parameters()

    @pytest.mark.unit_test
    def test_get_main_parameters_raises_exception_if_params_are_missing(self, tmp_path):
        empty_json = tmp_path / "dummy.json"
        config_yaml = tmp_path / "empty.yaml"
        config_yaml.write_text(
            'LOG_DIR : "LOGS"\n'
            'JSON_DIR : "JSON"\n'
            'STUDIES_IN_DIR : "STUDIES-IN"\n'
            'FINISHED_DIR : "FINISHED"\n'
            "DEFAULT_TIME_LIMIT : 172800\n"
            "DEFAULT_N_CPU : 2\n"
        )
        with pytest.raises(ParametersReader.MissingValueException):
            ParametersReader(empty_json, config_yaml).get_main_parameters()

    @pytest.mark.unit_test
    def test_get_option_parameters_initializes_parameters_correctly(self, tmp_path):
        empty_json = tmp_path / "dummy.json"
        empty_json.write_text("{}")
        config_yaml = tmp_path / "empty.yaml"
        config_yaml.write_text(self.yaml_compulsory_content)
        options_parameters = ParametersReader(
            empty_json, config_yaml
        ).get_parser_parameters()
        assert options_parameters.log_dir == self.LOG_DIR
        assert options_parameters.studies_in_dir == self.STUDIES_IN_DIR
        assert options_parameters.finished_dir == self.FINISHED_DIR
        assert options_parameters.default_time_limit == self.DEFAULT_TIME_LIMIT
        assert options_parameters.default_n_cpu == self.DEFAULT_N_CPU
        assert options_parameters.default_wait_time == self.DEFAULT_WAIT_TIME
        assert (
            options_parameters.ssh_config_file_is_required
            == self.SSH_CONFIG_FILE_IS_REQUIRED
        )
        alternate1 = Path.cwd() / self.DEFAULT_SSH_CONFIGFILE_NAME
        alternate2 = (
            Path.home() / "antares_launcher_settings" / self.DEFAULT_SSH_CONFIGFILE_NAME
        )
        assert options_parameters.ssh_configfile_path_alternate1 == alternate1
        assert options_parameters.ssh_configfile_path_alternate2 == alternate2

    @pytest.mark.unit_test
    def test_get_main_parameters_initializes_parameters_correctly(self, tmp_path):
        yaml_name = "dummy.yaml"
        config_yaml = tmp_path / yaml_name
        config_yaml.write_text(self.yaml_compulsory_content)
        empty_json = tmp_path / "dummy.json"
        empty_json.write_text("{}")
        main_parameters = ParametersReader(
            empty_json, config_yaml
        ).get_main_parameters()
        assert main_parameters.json_dir == Path(self.JSON_DIR)
        assert main_parameters.slurm_script_path == self.SLURM_SCRIPT_PATH
        assert (
            main_parameters.default_json_db_name
            == f"{getpass.getuser()}_antares_launcher_db.json"
        )
        assert main_parameters.db_primary_key == self.DB_PRIMARY_KEY
        assert not main_parameters.default_ssh_dict
        assert (
            main_parameters.antares_versions_on_remote_server
            == self.ANTARES_SUPPORTED_VERSIONS
        )

    @pytest.mark.unit_test
    def test_get_main_parameters_initializes_default_ssh_dict_correctly(self, tmp_path):
        config_yaml = tmp_path / "dummy.yaml"
        config_yaml.write_text(self.yaml_compulsory_content)
        ssh_json = tmp_path / "dummy.json"
        with open(ssh_json, "w") as file:
            json.dump(self.json_dict, file)

        main_parameters = ParametersReader(
            json_ssh_conf=ssh_json, yaml_filepath=config_yaml
        ).get_main_parameters()
        assert main_parameters.default_ssh_dict == self.json_dict
