import getpass
import re
import shlex
import socket
from pathlib import Path, PurePosixPath
from typing import List
from unittest import mock
from unittest.mock import call

import pytest

from antareslauncher.remote_environnement.remote_environment_with_slurm import (
    GetJobStateError,
    KillJobError,
    NoLaunchScriptFoundError,
    NoRemoteBaseDirError,
    RemoteEnvironmentWithSlurm,
    SubmitJobError,
)
from antareslauncher.remote_environnement.slurm_script_features import ScriptParametersDTO, SlurmScriptFeatures
from antareslauncher.study_dto import Modes, StudyDTO
from antares.study.version import StudyVersion


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
            path="path/to/study/91f1f911-4f4a-426f-b127-d0c2a2465b5f",
            n_cpu=42,
            zipfile_path="path/to/study/91f1f911-4f4a-426f-b127-d0c2a2465b5f-foo.zip",
            antares_version=StudyVersion.parse(700),
            local_final_zipfile_path="local_final_zipfile_path",
            run_mode=Modes.antares,
        )

    @pytest.fixture(scope="function")
    def remote_env(self) -> RemoteEnvironmentWithSlurm:
        """SLURM remote environment (Mock)"""
        remote_home_dir = "remote_home_dir"
        connection = mock.Mock(home_dir="path/to/home")
        connection.home_dir = remote_home_dir
        slurm_script_features = SlurmScriptFeatures(
            "slurm_script_path",
            partition="fake_partition",
            quality_of_service="user1_qos",
        )
        return RemoteEnvironmentWithSlurm(connection, slurm_script_features)

    @pytest.mark.unit_test
    def test_initialise_remote_path_calls_connection_make_dir_with_correct_arguments(
        self,
    ):
        # given
        remote_home_dir = "remote_home_dir"
        remote_base_dir = f"{remote_home_dir}/REMOTE_{getpass.getuser()}_{socket.gethostname()}"
        connection = mock.Mock(home_dir="path/to/home")
        connection.home_dir = remote_home_dir
        connection.make_dir = mock.Mock(return_value=True)
        connection.check_file_not_empty = mock.Mock(return_value=True)
        slurm_script_features = SlurmScriptFeatures(
            "slurm_script_path",
            partition="fake_partition",
            quality_of_service="user1_qos",
        )
        # when
        RemoteEnvironmentWithSlurm(connection, slurm_script_features)
        # then
        connection.make_dir.assert_called_with(remote_base_dir)

    @pytest.mark.unit_test
    def test_when_constructor_is_called_and_remote_base_path_cannot_be_created_then_exception_is_raised(
        self,
    ):
        # given
        connection = mock.Mock(home_dir="path/to/home")
        slurm_script_features = SlurmScriptFeatures(
            "slurm_script_path",
            partition="fake_partition",
            quality_of_service="user1_qos",
        )
        # when
        connection.make_dir = mock.Mock(return_value=False)
        # then
        with pytest.raises(NoRemoteBaseDirError):
            RemoteEnvironmentWithSlurm(connection, slurm_script_features)

    @pytest.mark.unit_test
    def test_when_constructor_is_called_then_connection_check_file_not_empty_is_called_with_correct_arguments(
        self,
    ):
        # given
        connection = mock.Mock(home_dir="path/to/home")
        connection.make_dir = mock.Mock(return_value=True)
        connection.check_file_not_empty = mock.Mock(return_value=True)
        slurm_script_features = SlurmScriptFeatures(
            "slurm_script_path",
            partition="fake_partition",
            quality_of_service="user1_qos",
        )
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
        connection = mock.Mock(home_dir="path/to/home")
        connection.home_dir = remote_home_dir
        connection.make_dir = mock.Mock(return_value=True)
        slurm_script_features = SlurmScriptFeatures(
            "slurm_script_path",
            partition="fake_partition",
            quality_of_service="user1_qos",
        )
        # when
        connection.check_file_not_empty = mock.Mock(return_value=False)
        # then
        with pytest.raises(NoLaunchScriptFoundError):
            RemoteEnvironmentWithSlurm(connection, slurm_script_features)

    @pytest.mark.unit_test
    def test_get_queue_info_calls_connection_execute_command_with_correct_argument(self, remote_env):
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
    def test_when_connection_exec_command_has_an_error_then_get_queue_info_returns_the_error_string(self, remote_env):
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
    def test_when_kill_remote_job_is_called_and_exec_command_returns_error_exception_is_raised(self, remote_env):
        # when
        output = None
        error = "error"
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        with pytest.raises(KillJobError):
            remote_env.kill_remote_job(42)

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_then_execute_command_is_called_with_specific_slurm_command(
        self, remote_env, study
    ):
        # the SSH call output should match "Submitted batch job (?P<job_id>\d+)"
        output = "Submitted batch job 456789\n"
        remote_env.connection.execute_command = mock.Mock(return_value=(output, ""))
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
        command = remote_env.slurm_script_features.compose_launch_command(remote_env.remote_base_path, script_params)
        remote_env.connection.execute_command.assert_called_once_with(command)

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_and_receives_submitted_420_returns_job_id_420(self, remote_env, study):
        # when
        output = "Submitted 420"
        error = None
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        assert remote_env.submit_job(study) == 420

    @pytest.mark.unit_test
    def test_when_submit_job_is_called_and_receives_error_then_exception_is_raised(self, remote_env, study):
        # when
        output = ""
        error = "error"
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        # then
        with pytest.raises(SubmitJobError):
            remote_env.submit_job(study)

    # noinspection SpellCheckingInspection
    @pytest.mark.unit_test
    def test_get_job_state_flags__scontrol_failed(self, remote_env, study):
        study.job_id = 42
        output, error = "", "invalid entity:XXX for keyword:show"
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        with pytest.raises(GetJobStateError, match=re.escape(error)) as ctx:
            remote_env.get_job_state_flags(study)
        assert output in str(ctx.value)
        command = f"scontrol show job {study.job_id}"
        remote_env.connection.execute_command.assert_called_once_with(command)

    # noinspection SpellCheckingInspection
    @pytest.mark.unit_test
    def test_get_job_state_flags__scontrol_dead_job(self, remote_env, study):
        study.job_id = 42
        job_state = "RUNNING"
        args = [
            "sacct",
            f"--jobs={study.job_id}",
            f"--name={study.name}",
            "--format=JobID,JobName,State",
            "--parsable2",
            "--delimiter=,",
            "--noheader",
        ]
        command = " ".join(shlex.quote(arg) for arg in args)

        # noinspection SpellCheckingInspection
        def execute_command_mock(cmd: str):
            if cmd == f"scontrol show job {study.job_id}":
                return "", "Invalid job id specified"
            if cmd == command:
                return f"{study.job_id},{study.name},{job_state}", None
            assert False, f"Unknown command: {cmd}"

        remote_env.connection.execute_command = execute_command_mock
        actual = remote_env.get_job_state_flags(study)
        assert actual == (True, False, False)

    # noinspection SpellCheckingInspection
    @pytest.mark.unit_test
    def test_get_job_state_flags__scontrol_nominal(self, remote_env, study):
        study.job_id = 42
        job_state = "RUNNING"
        output, error = f"JobState={job_state}", None
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        actual = remote_env.get_job_state_flags(study)
        assert actual == (True, False, False)

    # noinspection SpellCheckingInspection
    @pytest.mark.unit_test
    def test_get_job_state_flags__scontrol_non_parsable(self, remote_env, study):
        study.job_id = 42
        output, error = "Blah!Blah!", None
        remote_env.connection.execute_command = mock.Mock(return_value=(output, error))
        with pytest.raises(GetJobStateError, match="non-parsable output") as ctx:
            remote_env.get_job_state_flags(study)
        assert output in str(ctx.value)
        command = f"scontrol show job {study.job_id}"
        remote_env.connection.execute_command.assert_called_once_with(command)

    @pytest.mark.unit_test
    def test_get_job_state_flags__sacct_bad_output(self, remote_env, study):
        study.job_id = 42
        args = [
            "sacct",
            f"--jobs={study.job_id}",
            f"--name={study.name}",
            "--format=JobID,JobName,State",
            "--parsable2",
            "--delimiter=,",
            "--noheader",
        ]
        command = " ".join(shlex.quote(arg) for arg in args)

        # the output of `sacct` is not: JobID,JobName,State
        output = "the sun is shining"

        # noinspection SpellCheckingInspection
        def execute_command_mock(cmd: str):
            if cmd == f"scontrol show job {study.job_id}":
                return "", "Invalid job id specified"
            if cmd == command:
                return output, None
            assert False, f"Unknown command: {cmd}"

        remote_env.connection.execute_command = execute_command_mock

        with pytest.raises(GetJobStateError, match="non-parsable output") as ctx:
            remote_env.get_job_state_flags(study)
        assert output in str(ctx.value)

    # noinspection SpellCheckingInspection
    @pytest.mark.unit_test
    def test_get_job_state_flags__sacct_call_fails(self, remote_env, study):
        study.job_id = 42
        args = [
            "sacct",
            f"--jobs={study.job_id}",
            f"--name={study.name}",
            "--format=JobID,JobName,State",
            "--parsable2",
            "--delimiter=,",
            "--noheader",
        ]
        command = " ".join(shlex.quote(arg) for arg in args)

        # noinspection SpellCheckingInspection
        def execute_command_mock(cmd: str):
            if cmd == f"scontrol show job {study.job_id}":
                return "", "Invalid job id specified"
            if cmd == command:
                return None, "an error occurs"
            assert False, f"Unknown command: {cmd}"

        remote_env.connection.execute_command = execute_command_mock
        with pytest.raises(GetJobStateError, match="an error occurs"):
            remote_env.get_job_state_flags(study, attempts=2, sleep_time=0.1)
        remote_env.connection.execute_command.mock_calls = [
            call(command),
            call(command),
        ]

    # noinspection SpellCheckingInspection
    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "state, expected",
        [
            pytest.param("", (True, False, False), id="unknown-means-RUNNING"),
            ("PENDING", (False, False, False)),
            ("RUNNING", (True, False, False)),
            ("CANCELLED", (True, True, True)),
            ("CANCELLED by 123456", (True, True, True)),
            ("TIMEOUT", (True, True, True)),
            ("COMPLETED", (True, True, False)),
            ("COMPLETING", (True, False, False)),
            ("FAILED", (True, True, True)),
        ],
    )
    def test_get_job_state_flags__sacct_nominal_case(self, remote_env, study, state, expected):
        """
        Check that the "get_job_state_flags" method is correctly returning
        the status flags ("started", "finished", and "with_error")
        for a SLURM job in a specific state.
        """
        study.job_id = 42
        args = [
            "sacct",
            f"--jobs={study.job_id}",
            f"--name={study.name}",
            "--format=JobID,JobName,State",
            "--parsable2",
            "--delimiter=,",
            "--noheader",
        ]
        command = " ".join(shlex.quote(arg) for arg in args)

        # noinspection SpellCheckingInspection
        def execute_command_mock(cmd: str):
            if cmd == f"scontrol show job {study.job_id}":
                return "", "Invalid job id specified"
            if cmd == command:
                # the output of `sacct` should be: JobID,JobName,State
                output = f"{study.job_id},{study.name},{state}" if state else ""
                return output, None
            assert False, f"Unknown command: {cmd}"

        remote_env.connection.execute_command = execute_command_mock

        actual = remote_env.get_job_state_flags(study)
        assert actual == expected

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
    def test_given_a_study_when_remove_input_zipfile_then_connection_remove_file_is_called(self, remote_env, study):
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
        command = f"{remote_env.remote_base_path}/{Path(study.local_final_zipfile_path).name}"
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
    def test_given_a_study_when_clean_remote_server_called_then_remove_zip_methods_are_called(self, remote_env, study):
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
    def test_given_a_study_when_clean_remote_server_called_then_return_correct_result(self, remote_env, study):
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
        output = RemoteEnvironmentWithSlurm.convert_time_limit_from_seconds_to_minutes(time_lim_sec)
        # then
        assert output == 1

    @pytest.mark.parametrize(
        "job_type,mode,post_processing,other_options",
        [
            ("ANTARES_XPANSION_R", Modes.xpansion_r, True, ""),
            ("ANTARES_XPANSION_CPP", Modes.xpansion_cpp, True, ""),
            ("ANTARES", Modes.antares, True, "adq_patch_rc"),
            ("ANTARES_XPANSION_R", Modes.xpansion_r, False, ""),
            ("ANTARES_XPANSION_CPP", Modes.xpansion_cpp, False, ""),
            ("ANTARES", Modes.antares, False, ""),
            ("ANTARES", Modes.antares, False, 'xpress param-optim1="THREADS 4 PRESOLVE 1" solver-logs'),
        ],
    )
    @pytest.mark.unit_test
    def test_compose_launch_command(
        self,
        remote_env,
        job_type,
        mode,
        post_processing,
        other_options,
        study,
    ):
        # given
        filename_launch_script = remote_env.slurm_script_features.solver_script_path
        # when
        study.run_mode = mode
        study.post_processing = post_processing
        study.other_options = other_options
        script_params = ScriptParametersDTO(
            study_dir_name=Path(study.path).name,
            input_zipfile_name=Path(study.zipfile_path).name,
            time_limit=1,
            n_cpu=study.n_cpu,
            antares_version=study.antares_version,
            run_mode=study.run_mode,
            post_processing=study.post_processing,
            other_options=other_options,
        )
        command = remote_env.compose_launch_command(script_params)
        # then
        change_dir = f"cd {remote_env.remote_base_path}"
        reference_submit_command = (
            f"sbatch"
            " --partition=fake_partition"
            " --qos=user1_qos"
            f" --job-name={Path(study.path).name}"
            f" --time={study.time_limit // 60}"
            f" --cpus-per-task={study.n_cpu}"
            f" {filename_launch_script}"
            f" {Path(study.zipfile_path).name}"
            f" {study.antares_version:2d}"
            f" {job_type}"
            f" {post_processing}"
            f" '{other_options}'"
        )
        reference_command = f"{change_dir} && {reference_submit_command}"
        assert command.split() == reference_command.split()
        assert command == reference_command
