import getpass
import socket
from pathlib import Path, PurePosixPath
from typing import List
from unittest import mock
from unittest.mock import call

import pytest

from antareslauncher.remote_environnement.iremote_environment import (
    GetJobStateErrorException,
    GetJobStateOutputException,
    KillJobErrorException,
    NoLaunchScriptFoundException,
    NoRemoteBaseDirException,
    SubmitJobErrorException,
)
from antareslauncher.remote_environnement.remote_environment_with_slurm import (
    RemoteEnvironmentWithSlurm,
)
from antareslauncher.remote_environnement.slurm_script_features import (
    ScriptParametersDTO,
    SlurmScriptFeatures,
)
from antareslauncher.study_dto import Modes, StudyDTO


class TestRemoteEnvironmentWithSlurm:
    """
    Review all the tests for the Class RemoteEnvironmentWithSlurm

    Test the get_all_job_state_flags() method:

    2 given a study the output obtained from the SLURM command should be correctly interpreted
      (different tests should be created, one for each treated state): the return values
      of the methods should be correct

    3 given a study an exception should be raised (to be created in `iremote_environment.py`)
      if the execute_command fails

    4 given a study where `study.submitted` is not True we should define a return value
      (for example (false, false, false))

    5 given a study, if execute_command return an error then an exception should be raised

    6 if execute command return an output of length <=0 the same exception should be raised
    """

    @pytest.fixture(scope="function")
    def study(self) -> StudyDTO:
        """Dummy Study Data Transfer Object (DTO)"""
        return StudyDTO(
            time_limit=60,
            path="study path",
            n_cpu=42,
            zipfile_path="zipfile_path",
            antares_version="700",
            local_final_zipfile_path="local_final_zipfile_path",
            run_mode=Modes.antares,
        )

    @pytest.fixture(scope="function")
    def remote_env(self) -> RemoteEnvironmentWithSlurm:
        """SLURM remote environment (Mock)"""
        remote_home_dir = "remote_home_dir"
        connection = mock.Mock()
        connection.home_dir = remote_home_dir
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        return RemoteEnvironmentWithSlurm(connection, slurm_script_features)

    @pytest.mark.unit_test
    def test_initialise_remote_path_calls_connection_make_dir_with_correct_arguments(
        self,
    ):
        # given
        remote_home_dir = "remote_home_dir"
        remote_base_dir = (
            f"{remote_home_dir}/REMOTE_{getpass.getuser()}_{socket.gethostname()}"
        )
        connection = mock.Mock()
        connection.home_dir = remote_home_dir
        connection.make_dir = mock.Mock(return_value=True)
        connection.check_file_not_empty = mock.Mock(return_value=True)
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        # when
        RemoteEnvironmentWithSlurm(connection, slurm_script_features)
        # then
        connection.make_dir.assert_called_with(remote_base_dir)

    @pytest.mark.unit_test
    def test_when_constructor_is_called_and_remote_base_path_cannot_be_created_then_exception_is_raised(
        self,
    ):
        # given
        connection = mock.Mock()
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        # when
        connection.make_dir = mock.Mock(return_value=False)
        # then
        with pytest.raises(NoRemoteBaseDirException):
            RemoteEnvironmentWithSlurm(connection, slurm_script_features)

    @pytest.mark.unit_test
    def test_when_constructor_is_called_then_connection_check_file_not_empty_is_called_with_correct_arguments(
        self,
    ):
        # given
        connection = mock.Mock()
        connection.make_dir = mock.Mock(return_value=True)
        connection.check_file_not_empty = mock.Mock(return_value=True)
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        # when
        RemoteEnvironmentWithSlurm(connection, slurm_script_features)
        # then
        remote_script_antares = "slurm_script_path"
        connection.check_file_not_empty.assert_called_with(remote_script_antares)

    @pytest.mark.unit_test
    def test_when_constructor_is_called_and_connection_check_file_not_empty_is_false_then_exception_is_raised(
        self,
    ):
        # given
        remote_home_dir = "/applications/antares/"
        connection = mock.Mock()
        connection.home_dir = remote_home_dir
        connection.make_dir = mock.Mock(return_value=True)
        slurm_script_features = SlurmScriptFeatures("slurm_script_path")
        # when
        connection.check_file_not_empty = mock.Mock(return_value=False)
        # then
        with pytest.raises(NoLaunchScriptFoundException):
            RemoteEnvironmentWithSlurm(connection, slurm_script_features)

    @pytest.mark.unit_test
    def test_get_queue_info_calls_connection_execute_command_with_correct_argument(
        self, remote_env
    ):
        # given
        username = "username"
        host = "host"
        remote_env.connection.username = username
        remote_env.connection.host = host
        command = f"squeue -u {username} --Format=name:40,state:12,starttime:22,TimeUsed:12,timelimit:12"
        output = "output"
        error = None
        # when
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        assert remote_env.get_queue_info() == f"{username}@{host}\n{output}"
        remote_env.connection.execute_command.assert_called_with(command)

    @pytest.mark.unit_test
    def test_when_connection_exec_command_has_an_error_then_get_queue_info_returns_the_error_string(
        self, remote_env
    ):
        # given
        username = "username"
        remote_env.connection.username = username
        # when
        output = None
        error = "error"
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        assert remote_env.get_queue_info() == "error"

    # noinspection SpellCheckingInspection
    @pytest.mark.unit_test
    def test_kill_remote_job_execute_scancel_command(self, remote_env):
        job_id = 42
        output = None
        error = None
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        command = f"scancel {job_id}"
        remote_env.kill_remote_job(job_id)
        remote_env.connection.execute_command.assert_called_with(command)

    @pytest.mark.unit_test
    def test_when_kill_remote_job_is_called_and_exec_command_returns_error_exception_is_raised(
        self, remote_env
    ):
        # when
        output = None
        error = "error"
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        with pytest.raises(KillJobErrorException):
            remote_env.kill_remote_job(42)

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_then_execute_command_is_called_with_specific_slurm_command(
        self, remote_env, study
    ):
        # when
        output = "output"
        error = None
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        remote_env.submit_job(study)
        # then
        script_params = ScriptParametersDTO(
            study_dir_name=Path(study.path).name,
            input_zipfile_name=Path(study.zipfile_path).name,
            time_limit=1,
            n_cpu=study.n_cpu,
            antares_version=study.antares_version,
            run_mode=study.run_mode,
            post_processing=study.post_processing,
            other_options="",
        )
        command = remote_env.slurm_script_features.compose_launch_command(
            remote_env.remote_base_path, script_params
        )
        remote_env.connection.execute_command.assert_called_with(command)

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_and_receives_submitted_420_returns_job_id_420(
        self, remote_env, study
    ):
        # when
        output = "Submitted 420"
        error = None
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        assert remote_env.submit_job(study) == 420

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_and_receives_error_then_exception_is_raised(
        self, remote_env, study
    ):
        # when
        output = ""
        error = "error"
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        with pytest.raises(SubmitJobErrorException):
            remote_env.submit_job(study)

    @pytest.mark.unit_test
    def test_when_check_job_state_is_called_then_execute_command_is_called_with_correct_command(
        self, remote_env, study
    ):
        # given
        output = "output"
        error = ""
        study.submitted = True
        study.job_id = 42
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # when
        remote_env.get_job_state_flags(study)
        # then
        # noinspection SpellCheckingInspection
        expected_command = (
            f"sacct -j {study.job_id} -n --format=state | head -1 "
            + "| awk -F\" \" '{print $1}'"
        )
        remote_env.connection.execute_command.assert_called_with(expected_command)

    @pytest.mark.unit_test
    def test_given_submitted_study__when_check_job_state_gets_empty_output_it_tries_5_times_then_raises_exception(
        self, remote_env, study
    ):
        # given
        output = ""
        error = ""
        study.submitted = True
        study.job_id = 42
        # when
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        with pytest.raises(GetJobStateOutputException):
            remote_env.get_job_state_flags(study)
        tries_number = remote_env.connection.execute_command.call_count
        assert tries_number == 5

    @pytest.mark.unit_test
    def test_given_a_submitted_study_when_execute_command_returns_an_error_then_an_exception_is_raised(
        self, remote_env, study
    ):
        # given
        output = "output"
        error = "error"
        study.submitted = True
        study.job_id = 42
        # when
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        with pytest.raises(GetJobStateErrorException):
            remote_env.get_job_state_flags(study)

    # noinspection SpellCheckingInspection
    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "output,expected_started, expected_finished, expected_with_error",
        [
            ("PENDING", False, False, False),
            ("RUNNING", True, False, False),
            ("CANCELLED BY DUMMY", True, True, True),
            ("TIMEOUT", True, True, True),
            ("COMPLETED", True, True, False),
            ("FAILED DUMMYWORD", True, True, True),
        ],
    )
    def test_given_state_when_get_job_state_flags_is_called_then_started_and_finished_and_with_error_are_correct(
        self,
        remote_env,
        study,
        output,
        expected_started,
        expected_finished,
        expected_with_error,
    ):
        # given
        error = ""
        study.submitted = True
        study.job_id = 42
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # when
        (
            started,
            finished,
            with_error,
        ) = remote_env.get_job_state_flags(study)
        # then
        assert started is expected_started
        assert finished is expected_finished
        assert with_error is expected_with_error

    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "remote_files, local_files",
        [
            pytest.param(
                # list of files in the remote server
                [
                    "antares-err-999999999.txt",
                    "antares-out-999999999.txt",
                    "0372c064-66db-4dd6-a05f-74f0753340b4_job_data_999999999.txt",
                    "antares-err-123456789.txt",
                    "antares-out-123456789.txt",
                    "364ef7a8-e110-4a3c-a345-58640c5885b1_job_data_123456789.txt",
                ],
                # expected list of downloaded files
                [
                    "antares-err-999999999.txt",
                    "antares-out-999999999.txt",
                ],
                # expected return value: list of downloaded files
                id="nominal-case",
            ),
            pytest.param([], [], id="no-log-file-OK"),
            pytest.param([], [], id="no-log-file-ERROR"),
        ],
    )
    def test_download_logs(
        self,
        remote_env,
        study,
        remote_files: List[str],
        local_files: List[str],
    ):
        # given
        study.job_id = 999999999
        study.job_log_dir = "/path/to/LOGS"
        downloaded = [Path(study.job_log_dir).joinpath(f) for f in local_files]
        remote_env.connection.download_files = mock.Mock(return_value=downloaded)

        # when
        actual = remote_env.download_logs(study)

        # then
        assert actual == downloaded

        src_dir = PurePosixPath(remote_env.remote_base_path)
        dst_dir = Path(study.job_log_dir)
        assert remote_env.connection.download_files.mock_calls == [
            call(src_dir, dst_dir, "*999999999*.txt", remove=study.finished)
        ]

    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "remote_files, downloaded_file",
        [
            pytest.param(
                # list of files in the remote server
                [
                    "finished_364ef7a8-e110-4a3c-a345-58640c5885b1_999999999.zip",
                    "antares-err-123456789.txt",
                    "antares-out-123456789.txt",
                    "364ef7a8-e110-4a3c-a345-58640c5885b1_job_data_123456789.txt",
                ],
                # the downloaded file
                "finished_364ef7a8-e110-4a3c-a345-58640c5885b1_999999999.zip",
                # expected return value: list of downloaded files
                id="nominal-case",
            ),
            pytest.param(
                # list of files in the remote server
                [
                    "finished_XPANSION_364ef7a8-e110-4a3c-a345-58640c5885b1_999999999.zip",
                    "antares-err-123456789.txt",
                    "antares-out-123456789.txt",
                    "364ef7a8-e110-4a3c-a345-58640c5885b1_job_data_123456789.txt",
                ],
                # the downloaded file
                "finished_XPANSION_364ef7a8-e110-4a3c-a345-58640c5885b1_999999999.zip",
                # expected return value: list of downloaded files
                id="xpansion-case",
            ),
            pytest.param([], "", id="no-log-file-OK"),
            pytest.param([], "", id="no-log-file-ERROR"),
        ],
    )
    def test_download_final_zip(
        self,
        remote_env,
        study,
        tmp_path,
        remote_files: List[str],
        downloaded_file: str,
    ):
        # noinspection PyUnusedLocal
        def my_download_files(*args, **kwargs):
            if downloaded_file:
                tmp_path.joinpath(downloaded_file).touch()
                return [tmp_path.joinpath(downloaded_file)]
            return []

        # given
        study.job_id = 999999999
        study.output_dir = str(tmp_path)
        study.local_final_zipfile_path = ""  # not yet downloaded
        remote_env.connection.download_files = my_download_files

        # when
        actual = remote_env.download_final_zip(study)

        # then
        expected = tmp_path.joinpath(downloaded_file) if downloaded_file else None
        assert actual == expected

    @pytest.mark.unit_test
    def test_given_a_study_with_input_zipfile_removed_when_remove_input_zipfile_then_return_true(
        self, remote_env, study
    ):
        # given
        study.input_zipfile_removed = True
        # when
        output = remote_env.remove_input_zipfile(study)
        # then
        assert output is True

    @pytest.mark.unit_test
    def test_given_a_study_when_remove_input_zipfile_then_connection_remove_file_is_called(
        self, remote_env, study
    ):
        # given
        study.input_zipfile_removed = False
        study.zipfile_path = "zipfile_path"
        zip_name = Path(study.zipfile_path).name
        command = f"{remote_env.remote_base_path}/{zip_name}"
        # when
        remote_env.remove_input_zipfile(study)
        # then
        # noinspection PyUnresolvedReferences
        remote_env.connection.remove_file.assert_called_once_with(command)

    @pytest.mark.unit_test
    def test_given_a_study_when_input_zipfile_not_removed_and_connection_successfully_removed_file_then_return_true(
        self, remote_env, study
    ):
        # given
        study.input_zipfile_removed = False
        study.zipfile_path = "zipfile_path"
        remote_env.connection.remove_file = mock.Mock(return_value=True)
        # when
        output = remote_env.remove_input_zipfile(study)
        # then
        assert output is True

    @pytest.mark.unit_test
    def test_given_a_study_when_remove_remote_final_zipfile_then_connection_remove_file_is_called(
        self, remote_env, study
    ):
        # given
        study.input_zipfile_removed = False
        study.zipfile_path = "zipfile_path"
        command = (
            f"{remote_env.remote_base_path}/{Path(study.local_final_zipfile_path).name}"
        )
        remote_env.connection.execute_command = mock.Mock(return_value=("", ""))
        # when
        remote_env.remove_remote_final_zipfile(study)
        # then
        # noinspection PyUnresolvedReferences
        remote_env.connection.remove_file.assert_called_once_with(command)

    @pytest.mark.unit_test
    def test_given_a_study_with_clean_remote_server_when_clean_remote_server_called_then_return_false(
        self, remote_env, study
    ):
        # given
        study.remote_server_is_clean = True
        # when
        output = remote_env.clean_remote_server(study)
        # then
        assert output is False

    @pytest.mark.unit_test
    def test_given_a_study_when_clean_remote_server_called_then_remove_zip_methods_are_called(
        self, remote_env, study
    ):
        # given
        study.remote_server_is_clean = False
        remote_env.remove_remote_final_zipfile = mock.Mock(return_value=False)
        remote_env.remove_input_zipfile = mock.Mock(return_value=False)
        # when
        remote_env.clean_remote_server(study)
        # then
        remote_env.remove_remote_final_zipfile.assert_called_once_with(study)
        remote_env.remove_input_zipfile.assert_called_once_with(study)

    @pytest.mark.unit_test
    def test_given_a_study_when_clean_remote_server_called_then_return_correct_result(
        self, remote_env, study
    ):
        # given
        study.remote_server_is_clean = False
        remote_env.remove_remote_final_zipfile = mock.Mock(return_value=False)
        remote_env.remove_input_zipfile = mock.Mock(return_value=False)
        # when
        output = remote_env.clean_remote_server(study)
        # then
        assert output is False
        # given
        study.remote_server_is_clean = False
        remote_env.remove_remote_final_zipfile = mock.Mock(return_value=True)
        remote_env.remove_input_zipfile = mock.Mock(return_value=False)
        # when
        output = remote_env.clean_remote_server(study)
        # then
        assert output is False
        # given
        study.remote_server_is_clean = False
        remote_env.remove_remote_final_zipfile = mock.Mock(return_value=False)
        remote_env.remove_input_zipfile = mock.Mock(return_value=True)
        # when
        output = remote_env.clean_remote_server(study)
        # then
        assert output is False
        # given
        study.remote_server_is_clean = False
        remote_env.remove_remote_final_zipfile = mock.Mock(return_value=True)
        remote_env.remove_input_zipfile = mock.Mock(return_value=True)
        # when
        output = remote_env.clean_remote_server(study)
        # then
        assert output is True

    @pytest.mark.unit_test
    def test_given_time_limit_lower_than_min_duration_when_convert_time_is_called_return_min_duration(
        self,
    ):
        # given
        time_lim_sec = 42
        # when
        output = RemoteEnvironmentWithSlurm.convert_time_limit_from_seconds_to_minutes(
            time_lim_sec
        )
        # then
        assert output == 1

    @pytest.mark.parametrize(
        "job_type,mode,post_processing",
        [
            ("ANTARES_XPANSION_R", Modes.xpansion_r, True),
            ("ANTARES_XPANSION_CPP", Modes.xpansion_cpp, True),
            ("ANTARES", Modes.antares, True),
            ("ANTARES_XPANSION_R", Modes.xpansion_r, False),
            ("ANTARES_XPANSION_CPP", Modes.xpansion_cpp, False),
            ("ANTARES", Modes.antares, False),
        ],
    )
    @pytest.mark.unit_test
    def test_compose_launch_command(
        self,
        remote_env,
        job_type,
        mode,
        post_processing,
        study,
    ):
        # given
        filename_launch_script = remote_env.slurm_script_features.solver_script_path
        # when
        study.run_mode = mode
        study.post_processing = post_processing
        script_params = ScriptParametersDTO(
            study_dir_name=Path(study.path).name,
            input_zipfile_name=Path(study.zipfile_path).name,
            time_limit=1,
            n_cpu=study.n_cpu,
            antares_version=study.antares_version,
            run_mode=study.run_mode,
            post_processing=study.post_processing,
            other_options="",
        )
        command = remote_env.compose_launch_command(script_params)
        # then
        change_dir = f"cd {remote_env.remote_base_path}"
        reference_submit_command = (
            f"sbatch"
            f' --job-name="{Path(study.path).name}"'
            f" --time={study.time_limit // 60}"
            f" --cpus-per-task={study.n_cpu}"
            f" {filename_launch_script}"
            f' "{Path(study.zipfile_path).name}"'
            f" {study.antares_version}"
            f" {job_type}"
            f" {post_processing}"
            f" ''"
        )
        reference_command = f"{change_dir} && {reference_submit_command}"
        assert command.split() == reference_command.split()
        assert command == reference_command
