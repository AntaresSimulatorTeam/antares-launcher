from pathlib import Path

import pytest

from antareslauncher.main_option_parser import (
    MainOptionParser,
    ParserParameters,
)
from antareslauncher.main_option_parser import look_for_default_ssh_conf_file


class TestMainOptionParser:
    def setup_method(self):
        self.main_options_parameters = ParserParameters(
            default_wait_time=23,
            default_time_limit=24,
            default_n_cpu=42,
            studies_in_dir="studies_in_dir",
            log_dir="log_dir",
            finished_dir="finished_dir",
            ssh_config_file_is_required=True,
            ssh_configfile_path_alternate1=Path("ssh_configfile_path_prod_cwd"),
            ssh_configfile_path_alternate2=Path("ssh_configfile_path_prod_user"),
        )

        self.DEFAULT_VALUES = {
            "wait_mode": False,
            "wait_time": 23,
            "studies_in": "studies_in_dir",
            "output_dir": "finished_dir",
            "check_queue": False,
            "time_limit": 24,
            "log_dir": "log_dir",
            "n_cpu": 42,
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
