from pathlib import Path

import pytest

from antareslauncher import definitions
from antareslauncher.main_option_parser import MainOptionParser, MainOptionsParameters
from antareslauncher.main_option_parser import get_default_db_name
from antareslauncher.main_option_parser import look_for_default_ssh_conf_file


class TestMainOptionParser:
    def setup_method(self):
        self.main_options_parameters = MainOptionsParameters(
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

        self.DEFAULT_VALUES = {
            "wait_mode": False,
            "wait_time": definitions.DEFAULT_WAIT_TIME,
            "studies_in": str(definitions.STUDIES_IN_DIR),
            "output_dir": str(definitions.FINISHED_DIR),
            "check_queue": False,
            "time_limit": definitions.DEFAULT_TIME_LIMIT,
            "log_dir": str(definitions.LOG_DIR),
            "n_cpu": definitions.DEFAULT_N_CPU,
            "job_id_to_kill": None,
            "post_processing": False,
            "json_ssh_config": look_for_default_ssh_conf_file(
                self.main_options_parameters
            ),
        }

    @pytest.fixture(scope="function")
    def parser(self):
        return MainOptionParser(self.main_options_parameters)

    @pytest.mark.unit_test
    def test_check_all_default_values_are_present(self, parser):
        parser.add_basic_arguments()
        output = parser.parse_args([])
        out_dict = vars(output)
        for key, value in self.DEFAULT_VALUES.items():
            assert out_dict[key] == value

    @pytest.mark.unit_test
    def test_given_add_basic_arguments_all_default_values_are_present(self, parser):
        parser.add_basic_arguments()
        output = parser.parse_args([])
        out_dict = vars(output)
        for key, value in self.DEFAULT_VALUES.items():
            assert out_dict[key] == value

    @pytest.mark.unit_test
    def test_studies_in_get_correctly_set(self, parser):
        parser.add_basic_arguments()
        output = parser.parse_args(["--studies-in-dir=hello"])
        assert output.studies_in == "hello"
