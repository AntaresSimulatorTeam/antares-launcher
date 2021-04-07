import getpass
import socket
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher import definitions
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
    @pytest.mark.integration_test
    def test_given_2_studies_when_launch_controller_launch_all_studies_is_called_then_connection_upload_file_is_called_twice(
        self,
    ):
        # given
        connection = mock.Mock()
        slurm_script_features = SlurmScriptFeatures(definitions.SLURM_SCRIPT_PATH)
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
        # when
        launch_controller.launch_all_studies()

        # then
        assert connection.upload_file.call_count == 2

    @pytest.mark.integration_test
    def test_given_a_study_when_launch_controller_submit_job_is_called_then_connection_execute_command_is_called_once_with_correct_command(
        self,
    ):
        # given
        connection = mock.Mock()
        connection.execute_command = mock.Mock(return_value=["Submitted 42", ""])
        connection.home_dir = "Submitted"
        slurm_script_features = SlurmScriptFeatures(definitions.SLURM_SCRIPT_PATH)
        environment = RemoteEnvironmentWithSlurm(connection, slurm_script_features)
        study1 = StudyDTO(
            path="dummy_path",
            zipfile_path=str(Path("base_path") / "zip_name"),
            zip_is_sent=False,
            n_cpu=12,
            antares_version=700,
            time_limit=120,
        )
        home_dir = "Submitted"

        remote_base_path = (
            str(home_dir) + "/REMOTE_" + getpass.getuser() + "_" + socket.gethostname()
        )

        study_type = "ANTARES"
        post_processing = False
        command = (
            f"cd {remote_base_path} && "
            f'sbatch --job-name="{Path(study1.path).name}" --time={study1.time_limit // 60} --cpus-per-task={study1.n_cpu}'
            f" {environment.slurm_script_features.solver_script_path}"
            f' "{Path(study1.zipfile_path).name}" {study1.antares_version} {study_type} {post_processing}'
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
    def test_given_two_sent_studies_when_launch_all_studies_executed_then_remove_zip_file_is_called_twice(
        self,
    ):
        # given
        connection = mock.Mock()
        slurm_script_features = SlurmScriptFeatures(definitions.SLURM_SCRIPT_PATH)
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
            repo=data_repo, env=environment, file_manager=file_manager, display=display
        )
        launch_controller.file_manager.remove_file = mock.Mock()

        # when
        launch_controller.launch_all_studies()

        # then
        assert launch_controller.file_manager.remove_file.call_count == 2
