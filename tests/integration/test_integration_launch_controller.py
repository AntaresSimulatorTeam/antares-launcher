import getpass
import socket
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import (
    RemoteEnvironmentWithSlurm,
)
from antareslauncher.remote_environnement.slurm_script_features import (
    SlurmScriptFeatures,
)
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch.launch_controller import LaunchController


class TestIntegrationLaunchController:
    @pytest.fixture(scope="function")
    def launch_controller(self):
        connection = mock.Mock()
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        environment = RemoteEnvironmentWithSlurm(connection, slurm_script_features)
        study1 = mock.Mock()
        study1.zipfile_path = "filepath"
        study1.zip_is_sent = False
        study1.path = "path"
        study2 = mock.Mock()
        study2.zipfile_path = "filepath"
        study2.zip_is_sent = False
        study2.path = "path"

        data_repo = mock.Mock()
        data_repo.get_list_of_studies = mock.Mock(return_value=[study1, study2])
        file_manager = mock.Mock()
        display = DisplayTerminal()
        launch_controller = LaunchController(
            repo=data_repo,
            env=environment,
            file_manager=file_manager,
            display=display,
        )

        return launch_controller

    @pytest.mark.integration_test
    def test_upload_file__called_twice(self, launch_controller):
        """
        This test function checks if when launching two studies through the controller,
        the call to the 'launch_all_studies' method triggers the 'upload_file' method
        of the connection twice.
        """
        # when
        launch_controller.launch_all_studies()

        # then
        # noinspection PyUnresolvedReferences
        assert launch_controller.env.connection.upload_file.call_count == 2

    @pytest.mark.integration_test
    def test_execute_command__called_with_the_correct_parameters(
        self,
    ):
        """
        This test function checks if when launching a study through the controller,
        the call to the `submit_job` method triggers the `execute_command` method
        of the connection only once, with the correct command.
        """
        # given
        connection = mock.Mock()
        connection.execute_command = mock.Mock(return_value=["Submitted 42", ""])
        connection.home_dir = "Submitted"
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        environment = RemoteEnvironmentWithSlurm(connection, slurm_script_features)
        study1 = StudyDTO(
            path="dummy_path",
            zipfile_path=str(Path("base_path") / "zip_name"),
            zip_is_sent=False,
            n_cpu=12,
            antares_version="700",
            time_limit=120,
        )
        home_dir = "Submitted"

        remote_base_path = (
            str(home_dir) + "/REMOTE_" + getpass.getuser() + "_" + socket.gethostname()
        )

        zipfile_name = Path(study1.zipfile_path).name
        job_type = "ANTARES"
        post_processing = False
        other_options = ""
        bash_options = (
                f'"{zipfile_name}"'
                f" {study1.antares_version}"
                f" {job_type}"
                f" {post_processing}"
                f" '{other_options}'"
        )
        command = (
            f"cd {remote_base_path} && "
            f'sbatch --job-name="{Path(study1.path).name}"'
            f" --time={study1.time_limit // 60}"
            f" --cpus-per-task={study1.n_cpu}"
            f" {environment.slurm_script_features.solver_script_path}"
            f" {bash_options}"
        )

        data_repo = mock.Mock()
        data_repo.get_list_of_studies = mock.Mock(return_value=[study1])
        file_manager = mock.Mock()
        display = DisplayTerminal()
        launch_controller = LaunchController(
            repo=data_repo,
            env=environment,
            file_manager=file_manager,
            display=display,
        )
        # when
        launch_controller.launch_all_studies()  # _submit_job(study1)

        # then
        connection.execute_command.assert_called_once_with(command)

    @pytest.mark.integration_test
    def test_remove_zip_file__called_twice(self, launch_controller):
        """
        This test function checks if when executing the `launch_all_studies` with two sent studies,
        the `remove_zip_file` method is called twice.
        """
        launch_controller.file_manager.remove_file = mock.Mock()

        # when
        launch_controller.launch_all_studies()

        # then
        assert launch_controller.file_manager.remove_file.call_count == 2
