"""
This file will contain all Integration tests. Ie, global from start to finish tests
It needs a proper ssh configuration and working remote server
"""
import getpass
import os
import shutil
from pathlib import Path

import pytest

from antareslauncher import main, definitions
from antareslauncher.main import MainParameters
from antareslauncher.main_option_parser import MainOptionParser, MainOptionsParameters

DATA_4_TEST_DIR = Path(__file__).parent.parent / "data"
ANTARES_STUDY = DATA_4_TEST_DIR / "one_node_v7"
EXAMPLE_STUDIES_IN = DATA_4_TEST_DIR / "STUDIES-IN-FOR-TEST"


def is_empty(directory):
    if os.listdir(directory):
        return False
    else:
        return True


class TestEndToEnd:
    def setup_method(self):
        self.studies_in_path = Path.cwd() / "STUDIES-IN"
        self.finished_path = Path.cwd() / "FINISHED"
        self.log_path = Path.cwd() / "LOGS"
        self.json_db_file_path = (
            Path.cwd() / f"{getpass.getuser()}_antares_launcher_db.json"
        )
        self.main_parameters = MainParameters(
            json_dir=definitions.JSON_DIR,
            default_json_db_name=definitions.DEFAULT_JSON_DB_NAME,
            slurm_script_path=definitions.SLURM_SCRIPT_PATH,
            antares_versions_on_remote_server=definitions.ANTARES_VERSIONS_ON_REMOTE_SERVER,
            default_ssh_dict_from_embedded_json=definitions.DEFAULT_SSH_DICT_FROM_EMBEDDED_JSON,
            db_primary_key=definitions.DB_PRIMARY_KEY,
        )
        try:
            self.json_db_file_path.unlink()
        except FileNotFoundError:
            pass

        self.ssh_config_file_path = DATA_4_TEST_DIR / "sshconfig.json"

        main_options_parameters = MainOptionsParameters(
            default_wait_time=definitions.DEFAULT_WAIT_TIME,
            default_time_limit=definitions.DEFAULT_TIME_LIMIT,
            default_n_cpu=definitions.DEFAULT_N_CPU,
            studies_in_dir=definitions.STUDIES_IN_DIR,
            log_dir=definitions.LOG_DIR,
            finished_dir=definitions.FINISHED_DIR,
            ssh_config_file_is_required=definitions.SSH_CONFIG_FILE_IS_REQUIRED,
            ssh_configfile_path_prod_cwd=definitions.SSH_CONFIGFILE_PATH_PROD_CWD,
            ssh_configfile_path_prod_user=definitions.SSH_CONFIGFILE_PATH_PROD_USER,
        )
        self.parser: MainOptionParser = MainOptionParser(
            main_options_parameters=main_options_parameters
        )
        self.parser.add_basic_arguments()
        self.parser.add_advanced_arguments()

    def teardown_method(self):
        shutil.rmtree(self.finished_path)
        shutil.rmtree(self.log_path)
        self.json_db_file_path.unlink()

    @pytest.mark.end_to_end_test
    def test_when_run_on_an_empty_directory_the_tree_structure_is_initialised(self):
        arg_ssh_config = ["--ssh-settings-file", f"{str(self.ssh_config_file_path)}"]
        input_arguments = self.parser.parse_args(arg_ssh_config)

        main.run_with(input_arguments, self.main_parameters)

        assert self.studies_in_path.is_dir()
        assert self.finished_path.is_dir()
        assert self.log_path.is_dir()
        assert self.json_db_file_path.is_file()

    @pytest.mark.end_to_end_test
    def test_one_study_is_correctly_processed(self):
        arg_ssh_config = ["--ssh-settings-file", f"{str(self.ssh_config_file_path)}"]
        arg_wait_mode = ["-w"]
        arg_wait_time = ["--wait-time", "2"]
        arg_2_cpu = ["-n", "2"]
        arg_studies_in = ["-i", f"{str(EXAMPLE_STUDIES_IN)}"]
        arguments = (
            arg_ssh_config + arg_wait_mode + arg_wait_time + arg_2_cpu + arg_studies_in
        )
        input_arguments = self.parser.parse_args(arguments)

        main.run_with(input_arguments, self.main_parameters)

        assert not is_empty(self.finished_path / ANTARES_STUDY.name)
        assert not is_empty(self.finished_path / ANTARES_STUDY.name / "output")

    @pytest.mark.end_to_end_test
    def test_one_xpansion_study_is_correctly_processed(self):
        arg_ssh_config = ["--ssh-settings-file", f"{str(self.ssh_config_file_path)}"]
        arg_xpansion = ["-x"]
        arg_wait_mode = ["-w"]
        arg_wait_time = ["--wait-time", "2"]
        arg_2_cpu = ["-n", "2"]
        arg_studies_in = ["-i", f"{str(EXAMPLE_STUDIES_IN)}"]
        arguments = (
            arg_ssh_config
            + arg_xpansion
            + arg_wait_mode
            + arg_wait_time
            + arg_2_cpu
            + arg_studies_in
        )
        input_arguments = self.parser.parse_args(arguments)

        main.run_with(input_arguments, self.main_parameters)

        assert not is_empty(self.finished_path / ANTARES_STUDY.name)
        assert not is_empty(self.finished_path / ANTARES_STUDY.name / "output")
