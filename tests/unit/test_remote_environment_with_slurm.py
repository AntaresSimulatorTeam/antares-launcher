import getpass
import socket
from pathlib import Path
from unittest import mock

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
    def study(self):
        study = StudyDTO(
            time_limit=60,
            path="study path",
            n_cpu=42,
            zipfile_path="zipfile_path",
            antares_version="700",
            local_final_zipfile_path="local_final_zipfile_path",
            run_mode=Modes.antares,
        )
        return study

    @pytest.fixture(scope="function")
    def my_remote_env_with_slurm_mock(self):
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
            str(remote_home_dir)
            + "/REMOTE_"
            + getpass.getuser()
            + "_"
            + socket.gethostname()
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
        remote_home_dir = "/applis/antares/"
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
        self, my_remote_env_with_slurm_mock
    ):
        # given
        username = "username"
        host = "host"
        my_remote_env_with_slurm_mock.connection.username = username
        my_remote_env_with_slurm_mock.connection.host = host
        command = f"squeue -u {username} --Format=name:40,state:12,starttime:22,TimeUsed:12,timelimit:12"
        output = "output"
        error = None
        # when
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # then
        assert (
            my_remote_env_with_slurm_mock.get_queue_info()
            == f"{username}@{host}\n" + output
        )
        my_remote_env_with_slurm_mock.connection.execute_command.assert_called_with(
            command
        )

    @pytest.mark.unit_test
    def test_when_connection_exec_command_has_an_error_then_get_queue_info_returns_the_error_string(
        self, my_remote_env_with_slurm_mock
    ):
        # given
        username = "username"
        my_remote_env_with_slurm_mock.connection.username = username
        # when
        output = None
        error = "error"
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # then
        assert my_remote_env_with_slurm_mock.get_queue_info() is "error"

    @pytest.mark.unit_test
    def test_kill_remote_job_execute_scancel_command(
        self, my_remote_env_with_slurm_mock
    ):
        job_id = 42
        output = None
        error = None
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        command = f"scancel {job_id}"
        my_remote_env_with_slurm_mock.kill_remote_job(job_id)
        my_remote_env_with_slurm_mock.connection.execute_command.assert_called_with(
            command
        )

    @pytest.mark.unit_test
    def test_when_kill_remote_job_is_called_and_exec_command_returns_error_exception_is_raised(
        self, my_remote_env_with_slurm_mock
    ):
        # when
        output = None
        error = "error"
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # then
        with pytest.raises(KillJobErrorException):
            my_remote_env_with_slurm_mock.kill_remote_job(42)

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_then_execute_command_is_called_with_specific_slurm_command(
        self, my_remote_env_with_slurm_mock, study
    ):
        # when
        output = "output"
        error = None
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        my_remote_env_with_slurm_mock.submit_job(study)
        # then
        script_params = ScriptParametersDTO(
            study_dir_name=Path(study.path).name,
            input_zipfile_name=Path(study.zipfile_path).name,
            time_limit=60 // 60,
            n_cpu=study.n_cpu,
            antares_version=study.antares_version,
            run_mode=study.run_mode,
            post_processing=study.post_processing,
            other_options="",
        )
        command = (
            my_remote_env_with_slurm_mock.slurm_script_features.compose_launch_command(
                my_remote_env_with_slurm_mock.remote_base_path, script_params
            )
        )
        my_remote_env_with_slurm_mock.connection.execute_command.assert_called_with(
            command
        )

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_and_receives_submitted_420_returns_job_id_420(
        self, my_remote_env_with_slurm_mock, study
    ):
        # when
        output = "Submitted 420"
        error = None
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # then
        assert my_remote_env_with_slurm_mock.submit_job(study) == 420

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_and_receives_error_then_exception_is_raised(
        self, my_remote_env_with_slurm_mock, study
    ):
        # when
        output = ""
        error = "error"
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # then
        with pytest.raises(SubmitJobErrorException):
            my_remote_env_with_slurm_mock.submit_job(study)

    @pytest.mark.unit_test
    def test_when_check_job_state_is_called_then_execute_command_is_called_with_correct_command(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        output = "output"
        error = ""
        study.submitted = True
        study.job_id = 42
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # when
        my_remote_env_with_slurm_mock.get_job_state_flags(study)
        # then
        expected_command = (
            f"sacct -j {study.job_id} -n --format=state | head -1 "
            + "| awk -F\" \" '{print $1}'"
        )
        my_remote_env_with_slurm_mock.connection.execute_command.assert_called_with(
            expected_command
        )

    @pytest.mark.unit_test
    def test_given_submitted_study__when_check_job_state_gets_empty_output_it_tries_5_times_then_raises_exception(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        output = ""
        error = ""
        study.submitted = True
        study.job_id = 42
        # when
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # then
        with pytest.raises(GetJobStateOutputException):
            my_remote_env_with_slurm_mock.get_job_state_flags(study)
        tries_number = (
            my_remote_env_with_slurm_mock.connection.execute_command.call_count
        )
        assert tries_number == 5

    @pytest.mark.unit_test
    def test_given_a_submitted_study_when_execute_command_returns_an_error_then_an_exception_is_raised(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        output = "output"
        error = "error"
        study.submitted = True
        study.job_id = 42
        # when
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # then
        with pytest.raises(GetJobStateErrorException):
            my_remote_env_with_slurm_mock.get_job_state_flags(study)

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
        my_remote_env_with_slurm_mock,
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
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=(output, error)
        )
        # when
        (
            started,
            finished,
            with_error,
        ) = my_remote_env_with_slurm_mock.get_job_state_flags(study)
        # then
        assert started is expected_started
        assert finished is expected_finished
        assert with_error is expected_with_error

    @pytest.mark.unit_test
    def test_given_a_not_started_study_when_list_remote_logs_is_called_then_returns_empty_list(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.started = False
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=("", "")
        )

        # when
        output = my_remote_env_with_slurm_mock._list_remote_logs(study)

        # then
        assert output == []

    @pytest.mark.unit_test
    def test_given_a_started_study_when_list_remote_logs_is_called_then_connection_execute_command_is_called_with_right_argument(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.job_id = 24
        study.started = True
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=("", "")
        )
        command = (
            f"ls  {my_remote_env_with_slurm_mock.remote_base_path}/*{study.job_id}*.txt"
        )

        # when
        my_remote_env_with_slurm_mock._list_remote_logs(study.job_id)

        # then
        my_remote_env_with_slurm_mock.connection.execute_command.assert_called_once_with(
            command
        )

    @pytest.mark.unit_test
    def test_given_a_started_study_when_list_remote_logs_is_called_and_execute_command_produces_error_then_returns_empty_list(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.started = True
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=("output", "error")
        )

        # when
        output = my_remote_env_with_slurm_mock._list_remote_logs(study)

        # then
        assert output == []

    @pytest.mark.unit_test
    def test_given_a_started_study_when_list_remote_logs_is_called_and_execute_command_produces_no_output_then_returns_empty_list(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.started = True
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=("", "")
        )

        # when
        output = my_remote_env_with_slurm_mock._list_remote_logs(study)

        # then
        assert output == []

    @pytest.mark.unit_test
    def test_given_a_started_study_when_list_remote_logs_is_called_then_returns_not_empty_list(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.started = True
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=("output", "")
        )

        # when
        output = my_remote_env_with_slurm_mock._list_remote_logs(study)

        # then
        assert output

    @pytest.mark.unit_test
    def test_given_a_study_when_download_logs_is_called_then_list_remote_logs_is_called(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        my_remote_env_with_slurm_mock._list_remote_logs = mock.Mock(return_value=[])

        # when
        my_remote_env_with_slurm_mock.download_logs(study)

        # then
        my_remote_env_with_slurm_mock._list_remote_logs.assert_called_once_with(
            study.job_id
        )

    @pytest.mark.unit_test
    def test_given_an_empty_file_list_when_download_logs_is_called_then_connection_download_files_is_not_called(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        my_remote_env_with_slurm_mock._list_remote_logs = mock.Mock(return_value=[])
        my_remote_env_with_slurm_mock.connection.download_file = mock.Mock()

        # when
        return_flag = my_remote_env_with_slurm_mock.download_logs(study)

        # then
        my_remote_env_with_slurm_mock.connection.download_file.assert_not_called()
        assert return_flag is False

    @pytest.mark.unit_test
    def test_given_a_file_list_when_download_logs_is_called_then_connection_download_files_is_called_with_correct_arguments(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.job_log_dir = "job_log_dir"
        file_path = "file"
        my_remote_env_with_slurm_mock._list_remote_logs = mock.Mock(
            return_value=[file_path]
        )
        my_remote_env_with_slurm_mock.connection.download_file = mock.Mock()

        src = my_remote_env_with_slurm_mock.remote_base_path + "/" + file_path
        dst = str(Path(study.job_log_dir) / file_path)

        # when
        my_remote_env_with_slurm_mock.download_logs(study)

        # then
        my_remote_env_with_slurm_mock.connection.download_file.assert_called_once_with(
            src, dst
        )

    @pytest.mark.unit_test
    def test_given_a_not_clean_study_and_a_file_list_with_two_elements_when_download_logs_is_called_then_connection_download_files_is_called_twice(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.remote_server_is_clean = False
        study.job_log_dir = "job_log_dir"
        my_remote_env_with_slurm_mock._list_remote_logs = mock.Mock(
            return_value=["file_path", "file_path2"]
        )
        my_remote_env_with_slurm_mock.connection.download_file = mock.Mock(
            return_value=True
        )

        # when
        return_flag = my_remote_env_with_slurm_mock.download_logs(study)

        # then
        my_remote_env_with_slurm_mock.connection.download_file.assert_called()
        assert my_remote_env_with_slurm_mock.connection.download_file.call_count == 2
        assert return_flag is True

    @pytest.mark.unit_test
    def test_given_a_not_finished_study_when_check_final_zip_not_empty_then_returns_false(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.finished = False
        final_zip_name = "final_zip_name"
        # when
        return_flag = my_remote_env_with_slurm_mock.check_final_zip_not_empty(
            study, final_zip_name
        )
        # then
        assert return_flag is False

    @pytest.mark.unit_test
    def test_given_a_finished_study_when_check_final_zip_not_empty_then_check_file_not_empty_is_called(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.finished = True
        final_zip_name = "final_zip_name"
        my_remote_env_with_slurm_mock.connection.check_file_not_empty = mock.Mock()
        # when
        my_remote_env_with_slurm_mock.check_final_zip_not_empty(study, final_zip_name)
        # then
        my_remote_env_with_slurm_mock.connection.check_file_not_empty.assert_called_once()

    @pytest.mark.unit_test
    def test_given_a_finished_study_with_empty_file_when_check_final_zip_not_empty_then_return_false(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.finished = True
        final_zip_name = "final_zip_name"
        my_remote_env_with_slurm_mock.connection.check_file_not_empty = mock.Mock(
            return_value=False
        )
        # when
        return_flag = my_remote_env_with_slurm_mock.check_final_zip_not_empty(
            study, final_zip_name
        )
        # then
        assert return_flag is False

    @pytest.mark.unit_test
    def test_given_a_finished_study_with_not_empty_file_when_check_final_zip_not_empty_then_return_true(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.finished = True
        final_zip_name = "final_zip_name"
        my_remote_env_with_slurm_mock.connection.check_file_not_empty = mock.Mock(
            return_value=True
        )
        # when
        return_flag = my_remote_env_with_slurm_mock.check_final_zip_not_empty(
            study, final_zip_name
        )
        # then
        assert return_flag is True

    @pytest.mark.unit_test
    def test_given_a_study_when_download_final_zip_is_called_then_check_final_zip_not_empty_is_called_with_correct_argument(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.path = "path"
        study.job_id = 1234
        final_zip_name = "finished_" + study.name + "_" + str(study.job_id) + ".zip"
        my_remote_env_with_slurm_mock.check_final_zip_not_empty = mock.Mock()
        # when
        my_remote_env_with_slurm_mock.download_final_zip(study)
        # then
        my_remote_env_with_slurm_mock.check_final_zip_not_empty.assert_called_once_with(
            study, final_zip_name
        )

    @pytest.mark.unit_test
    def test_given_a_study_with_empty_final_zip_when_download_final_zip_is_called_then_return_none(
        self, study, my_remote_env_with_slurm_mock
    ):
        # given
        study.path = "path"
        study.job_id = 1234
        my_remote_env_with_slurm_mock.connection.check_file_not_empty = mock.Mock(
            return_value=False
        )
        # when
        return_value = my_remote_env_with_slurm_mock.download_final_zip(study)
        # then
        assert return_value is None

    @pytest.mark.unit_test
    def test_given_a_study_with_final_zip_already_downloaded_when_download_final_zip_is_called_then_return_local_final_zipfile_path(
        self, study, my_remote_env_with_slurm_mock
    ):
        # given
        study.path = "path"
        study.job_id = 1234
        study.local_final_zipfile_path = "local_final_zipfile_path"
        my_remote_env_with_slurm_mock.check_final_zip_not_empty = mock.Mock(
            return_value=True
        )
        # when
        return_value = my_remote_env_with_slurm_mock.download_final_zip(study)
        # then
        assert return_value == study.local_final_zipfile_path

    @pytest.mark.unit_test
    def test_given_a_study_with_final_zip_when_download_final_zip_is_called_then_download_file_is_called_with_correct_argument(
        self, study, my_remote_env_with_slurm_mock
    ):
        # given
        study.finished = True
        study.job_id = 1234
        study.local_final_zipfile_path = ""
        final_zip_name = (
            "finished_" + Path(study.path).name + "_" + str(study.job_id) + ".zip"
        )
        my_remote_env_with_slurm_mock.connection.check_file_not_empty = mock.Mock(
            return_value=True
        )
        my_remote_env_with_slurm_mock.connection.download_file = mock.Mock()
        local_final_zipfile_path = str(Path(study.output_dir) / final_zip_name)
        src = my_remote_env_with_slurm_mock.remote_base_path + "/" + final_zip_name
        dst = str(local_final_zipfile_path)
        # when
        my_remote_env_with_slurm_mock.download_final_zip(study)
        # then
        my_remote_env_with_slurm_mock.connection.download_file.assert_called_once_with(
            src, dst
        )

    @pytest.mark.unit_test
    def test_given_a_study_with_final_zip_when_download_final_zip_is_called_and_file_is_not_downloaded_then_returns_none(
        self, study, my_remote_env_with_slurm_mock
    ):
        # given
        study.path = "path"
        study.job_id = 1234
        study.local_final_zipfile_path = ""
        my_remote_env_with_slurm_mock.check_file_not_empty = mock.Mock(
            return_value=True
        )
        my_remote_env_with_slurm_mock.connection.download_file = mock.Mock(
            return_value=False
        )
        # when
        return_value = my_remote_env_with_slurm_mock.download_final_zip(study)
        # then
        assert return_value is None

    @pytest.mark.unit_test
    def test_given_a_study_with_final_zip_when_download_final_zip_is_called_and_file_is_downloaded_then_returns_local_zipfile_path(
        self, study, my_remote_env_with_slurm_mock
    ):
        # given
        study.finished = True
        study.job_id = 1234
        final_zip_name = (
            "finished_" + Path(study.path).name + "_" + str(study.job_id) + ".zip"
        )
        local_final_zipfile_path = str(Path(study.output_dir) / final_zip_name)
        study.local_final_zipfile_path = ""
        my_remote_env_with_slurm_mock.connection.check_file_not_empty = mock.Mock(
            return_value=True
        )
        my_remote_env_with_slurm_mock.connection.download_file = mock.Mock(
            return_value=True
        )
        # when
        return_value = my_remote_env_with_slurm_mock.download_final_zip(study)
        # then
        assert return_value == local_final_zipfile_path

    @pytest.mark.unit_test
    def test_given_a_study_with_input_zipfile_removed_when_remove_input_zipfile_then_return_true(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.input_zipfile_removed = True
        # when
        output = my_remote_env_with_slurm_mock.remove_input_zipfile(study)
        # then
        assert output is True

    @pytest.mark.unit_test
    def test_given_a_study_when_remove_input_zipfile_then_connection_remove_file_is_called(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.input_zipfile_removed = False
        study.zipfile_path = "zipfile_path"
        zip_name = Path(study.zipfile_path).name
        command = f"{my_remote_env_with_slurm_mock.remote_base_path}/{zip_name}"
        # when
        my_remote_env_with_slurm_mock.remove_input_zipfile(study)
        # then
        my_remote_env_with_slurm_mock.connection.remove_file.assert_called_once_with(
            command
        )

    @pytest.mark.unit_test
    def test_given_a_study_when_input_zipfile_not_removed_and_connection_successfully_removed_file_then_return_true(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.input_zipfile_removed = False
        study.zipfile_path = "zipfile_path"
        my_remote_env_with_slurm_mock.connection.remove_file = mock.Mock(
            return_value=True
        )
        # when
        output = my_remote_env_with_slurm_mock.remove_input_zipfile(study)
        # then
        assert output is True

    @pytest.mark.unit_test
    def test_given_a_study_when_remove_remote_final_zipfile_then_connection_remove_file_is_called(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.input_zipfile_removed = False
        study.zipfile_path = "zipfile_path"
        command = f"{my_remote_env_with_slurm_mock.remote_base_path}/{Path(study.local_final_zipfile_path).name}"
        my_remote_env_with_slurm_mock.connection.execute_command = mock.Mock(
            return_value=("", "")
        )
        # when
        my_remote_env_with_slurm_mock.remove_remote_final_zipfile(study)
        # then
        my_remote_env_with_slurm_mock.connection.remove_file.assert_called_once_with(
            command
        )

    @pytest.mark.unit_test
    def test_given_a_study_with_clean_remote_server_when_clean_remote_server_called_then_return_false(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.remote_server_is_clean = True
        # when
        output = my_remote_env_with_slurm_mock.clean_remote_server(study)
        # then
        assert output is False

    @pytest.mark.unit_test
    def test_given_a_study_when_clean_remote_server_called_then_remove_zip_methods_are_called(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.remote_server_is_clean = False
        my_remote_env_with_slurm_mock.remove_remote_final_zipfile = mock.Mock(
            return_value=False
        )
        my_remote_env_with_slurm_mock.remove_input_zipfile = mock.Mock(
            return_value=False
        )
        # when
        my_remote_env_with_slurm_mock.clean_remote_server(study)
        # then
        my_remote_env_with_slurm_mock.remove_remote_final_zipfile.assert_called_once_with(
            study
        )
        my_remote_env_with_slurm_mock.remove_input_zipfile.assert_called_once_with(
            study
        )

    @pytest.mark.unit_test
    def test_given_a_study_when_clean_remote_server_called_then_return_correct_result(
        self, my_remote_env_with_slurm_mock, study
    ):
        # given
        study.remote_server_is_clean = False
        my_remote_env_with_slurm_mock.remove_remote_final_zipfile = mock.Mock(
            return_value=False
        )
        my_remote_env_with_slurm_mock.remove_input_zipfile = mock.Mock(
            return_value=False
        )
        # when
        output = my_remote_env_with_slurm_mock.clean_remote_server(study)
        # then
        assert output is False
        # given
        study.remote_server_is_clean = False
        my_remote_env_with_slurm_mock.remove_remote_final_zipfile = mock.Mock(
            return_value=True
        )
        my_remote_env_with_slurm_mock.remove_input_zipfile = mock.Mock(
            return_value=False
        )
        # when
        output = my_remote_env_with_slurm_mock.clean_remote_server(study)
        # then
        assert output is False
        # given
        study.remote_server_is_clean = False
        my_remote_env_with_slurm_mock.remove_remote_final_zipfile = mock.Mock(
            return_value=False
        )
        my_remote_env_with_slurm_mock.remove_input_zipfile = mock.Mock(
            return_value=True
        )
        # when
        output = my_remote_env_with_slurm_mock.clean_remote_server(study)
        # then
        assert output is False
        # given
        study.remote_server_is_clean = False
        my_remote_env_with_slurm_mock.remove_remote_final_zipfile = mock.Mock(
            return_value=True
        )
        my_remote_env_with_slurm_mock.remove_input_zipfile = mock.Mock(
            return_value=True
        )
        # when
        output = my_remote_env_with_slurm_mock.clean_remote_server(study)
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
        my_remote_env_with_slurm_mock,
        job_type,
        mode,
        post_processing,
        study,
    ):
        # given
        filename_launch_script = (
            my_remote_env_with_slurm_mock.slurm_script_features.solver_script_path
        )
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
        )
        command = my_remote_env_with_slurm_mock.compose_launch_command(script_params)
        # then
        change_dir = f"cd {my_remote_env_with_slurm_mock.remote_base_path}"
        reference_submit_command = f'sbatch --job-name="{Path(study.path).name}" --time={study.time_limit//60} --cpus-per-task={study.n_cpu} {filename_launch_script} "{Path(study.zipfile_path).name}" {study.antares_version} {job_type} {post_processing}'
        reference_command = change_dir + " && " + reference_submit_command
        assert command.split() == reference_command.split()
        assert command == reference_command
