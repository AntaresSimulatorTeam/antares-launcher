"""
This file will contain all Integration tests. Ie, global from start to finish tests
It needs a proper ssh configuration and working remote server
"""

import contextlib
import getpass
import os
import shutil
from pathlib import Path

import pytest

from antareslauncher import main
from antareslauncher.main import MainParameters
from antareslauncher.main_option_parser import (MainOptionParser,
                                                ParserParameters)
from antareslauncher.parameters_reader import ParametersReader
from tests.data import DATA_DIR


def get_test_config():
    return (DATA_DIR / "configuration.yaml").exists()


# You should define the `ANTARES_LAUNCHER_CONFIG_PATH` environment variable
# to run end-to-end tests. This variable should point to your "configuration.yaml" file.
TEST_CONFIG = get_test_config()

ANTARES_STUDY = DATA_DIR / "STUDIES-IN-FOR-TEST" / "one_node_v7"
EXAMPLE_STUDIES_IN = DATA_DIR / "STUDIES-IN-FOR-TEST"
SSH_JSON_FILE = DATA_DIR / "sshconfig.json"
YAML_CONF_FILE = DATA_DIR / "configuration.yaml"


class TestEndToEnd:
    def setup_method(self):
        self.studies_in_path = Path.cwd() / "STUDIES-IN"
        self.finished_path = Path.cwd() / "FINISHED"
        self.log_path = Path.cwd() / "LOGS"
        self.json_db_file_path = (
            Path.cwd() / f"{getpass.getuser()}_antares_launcher_db.json"
        )
        with contextlib.suppress(FileNotFoundError):
            self.json_db_file_path.unlink()
        param_reader = ParametersReader(
            json_ssh_conf=SSH_JSON_FILE, yaml_filepath=YAML_CONF_FILE
        )
        parser_parameters: ParserParameters = param_reader.get_parser_parameters()
        self.parser: MainOptionParser = MainOptionParser(parameters=parser_parameters)
        self.parser.add_basic_arguments().add_advanced_arguments()
        self.main_parameters: MainParameters = param_reader.get_main_parameters()

    def teardown_method(self):
        shutil.rmtree(self.finished_path)
        shutil.rmtree(self.log_path)
        self.json_db_file_path.unlink()

    @pytest.mark.end_to_end_test
    @pytest.mark.skipif(
        not TEST_CONFIG,
        reason="end-to-end config not found: read 'config.md' for more info",
    )
    def test_when_run_on_an_empty_directory_the_tree_structure_is_initialised(
        self,
    ):
        input_arguments = self.parser.parse_args([])

        main.run_with(input_arguments, self.main_parameters)

        assert self.studies_in_path.is_dir()
        assert self.finished_path.is_dir()
        assert self.log_path.is_dir()
        assert self.json_db_file_path.is_file()

    @pytest.mark.end_to_end_test
    @pytest.mark.skipif(
        not TEST_CONFIG,
        reason="end-to-end config not found: read 'config.md' for more info",
    )
    def test_one_study_is_correctly_processed(self):
        arg_wait_mode = ["-w"]
        arg_wait_time = ["--wait-time", "2"]
        arg_2_cpu = ["-n", "2"]
        arg_studies_in = ["-i", f"{str(EXAMPLE_STUDIES_IN)}"]
        arguments = arg_wait_mode + arg_wait_time + arg_2_cpu + arg_studies_in
        input_arguments = self.parser.parse_args(arguments)

        main.run_with(input_arguments, self.main_parameters)

        assert os.listdir(self.finished_path / ANTARES_STUDY.name)
        assert os.listdir(self.finished_path / ANTARES_STUDY.name / "output")

    @pytest.mark.end_to_end_test
    @pytest.mark.skipif(
        not TEST_CONFIG,
        reason="end-to-end config not found: read 'config.md' for more info",
    )
    def test_one_xpansion_study_is_correctly_processed(self):
        arg_xpansion = ["-x", "r"]
        arg_wait_mode = ["-w"]
        arg_wait_time = ["--wait-time", "2"]
        arg_2_cpu = ["-n", "2"]
        arg_studies_in = ["-i", f"{str(EXAMPLE_STUDIES_IN)}"]
        arguments = (
            arg_xpansion + arg_wait_mode + arg_wait_time + arg_2_cpu + arg_studies_in
        )
        input_arguments = self.parser.parse_args(arguments)

        main.run_with(input_arguments, self.main_parameters)

        assert os.listdir(self.finished_path / ANTARES_STUDY.name)
        assert os.listdir(self.finished_path / ANTARES_STUDY.name / "output")
