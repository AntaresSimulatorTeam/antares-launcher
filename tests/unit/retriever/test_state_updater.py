from pathlib import Path
from unittest import mock
from unittest.mock import call

import pytest

from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater


@pytest.mark.unit_test
@pytest.mark.parametrize(
    "started_flag,finished_flag,with_error_flag,status",
    [
        (False, False, False, "Pending"),
        (True, False, False, "Running"),
        (True, True, False, "Finished"),
        (None, None, True, "Ended with error"),
    ],
)
def test_given_a_submitted_study_then_study_flags_are_updated(
    started_flag, finished_flag, with_error_flag, status
):
    # given
    my_study = StudyDTO(path="study_path", job_id=42)
    remote_env_mock = mock.Mock()
    display = mock.Mock()
    remote_env_mock.get_job_state_flags = mock.Mock(
        return_value=(started_flag, finished_flag, with_error_flag)
    )
    display.show_message = mock.Mock()
    state_updater = StateUpdater(remote_env_mock, display)
    message = f'"{Path(my_study.path).name}"  (JOBID={my_study.job_id}): {status}'
    # when
    study_test = state_updater.run(my_study)
    # then
    remote_env_mock.get_job_state_flags.assert_called_once_with(my_study)
    display.show_message.assert_called_once_with(message, mock.ANY)
    assert study_test.started == started_flag
    assert study_test.finished == finished_flag
    assert study_test.with_error == with_error_flag
    assert study_test.job_state == status


@pytest.mark.unit_test
def test_given_a_non_submitted_study_then_get_job_state_flags_is_not_called():
    # given
    my_study = StudyDTO(path="study_path", job_id=None)
    remote_env_mock = mock.Mock()
    remote_env_mock.get_job_state_flags = mock.Mock()
    display = mock.Mock()
    display.show_error = mock.Mock()
    state_updater = StateUpdater(remote_env_mock, display)
    message = f'"{Path(my_study.path).name}": Job was not submitted'
    # when
    state_updater.run(my_study)
    # then
    remote_env_mock.get_job_state_flags.assert_not_called()
    display.show_error.assert_called_once_with(message, mock.ANY)


@pytest.mark.unit_test
def test_given_a_done_study_then_get_job_state_flags_is_not_called():
    # given
    my_study = StudyDTO(path="study_path", job_id=42, done=True)
    remote_env_mock = mock.Mock()
    remote_env_mock.get_job_state_flags = mock.Mock(return_value=(True, False, False))
    display = mock.Mock()
    display.show_message = mock.Mock()
    state_updater = StateUpdater(remote_env_mock, display)
    message = (
        f'"{Path(my_study.path).name}"  (JOBID={my_study.job_id}): everything is done'
    )
    # when
    state_updater.run(my_study)
    # then
    remote_env_mock.get_job_state_flags.assert_not_called()
    display.show_message.assert_called_once_with(message, mock.ANY)


@pytest.mark.unit_test
def test_state_updater_run_on_empty_list_of_studies_write_one_message():
    # given
    study_list = []
    remote_env_mock = mock.Mock()
    display = mock.Mock()
    state_updater = StateUpdater(remote_env_mock, display)
    message = "Checking status of the studies:"
    # when
    state_updater.run_on_list(study_list)
    # then
    display.show_message.assert_called_once_with(message, mock.ANY)


@pytest.mark.unit_test
def test_with_a_list_of_one_submitted_study_run_on_list_calls_run_once_on_study():
    # given
    my_study1 = StudyDTO(path="study_path1", job_id=1)
    study_list = [my_study1]
    remote_env_mock = mock.Mock()
    remote_env_mock.get_job_state_flags = mock.Mock(return_value=(1, 2, 3))
    display = mock.Mock()
    state_updater = StateUpdater(remote_env_mock, display)
    # when
    state_updater.run_on_list(study_list)
    # then
    remote_env_mock.get_job_state_flags.assert_called_once_with(my_study1)


@pytest.mark.unit_test
def test_run_on_list_calls_run_on_all_submitted_studies_of_the_list():
    # given
    my_study1 = StudyDTO(path="study_path1", job_id=1)
    my_study2 = StudyDTO(path="study_path2", job_id=None)
    my_study3 = StudyDTO(path="study_path3", job_id=2)
    study_list = [my_study1, my_study2, my_study3]
    remote_env_mock = mock.Mock()
    remote_env_mock.get_job_state_flags = mock.Mock(return_value=(1, 2, 3))
    display = mock.Mock()
    state_updater = StateUpdater(remote_env_mock, display)
    # when
    state_updater.run_on_list(study_list)
    # then
    calls = [call(my_study1), call(my_study3)]
    remote_env_mock.get_job_state_flags.assert_has_calls(calls)


@pytest.mark.unit_test
def test_run_on_list_calls_run_start__processing_studies_that_are_done():
    # given
    my_study1 = StudyDTO(path="study_path1", job_id=1, done=False)
    my_study2 = StudyDTO(path="study_path2", job_id=None)
    my_study3 = StudyDTO(path="study_path3", job_id=2, done=True)
    study_list = [my_study1, my_study2, my_study3]
    remote_env_mock = mock.Mock()
    remote_env_mock.get_job_state_flags = mock.Mock(return_value=(True, False, False))
    display = mock.Mock()
    display.show_message = mock.Mock()
    state_updater = StateUpdater(remote_env_mock, display)
    # when
    state_updater.run_on_list(study_list)
    # then
    welcome_message = "Checking status of the studies:"
    message1 = f'"{Path(my_study1.path).name}"  (JOBID={my_study1.job_id}): Running'
    message3 = (
        f'"{Path(my_study3.path).name}"  (JOBID={my_study3.job_id}): everything is done'
    )
    calls = [
        call(welcome_message, mock.ANY),
        call(message3, mock.ANY),
        call(message1, mock.ANY),
    ]
    display.show_message.assert_has_calls(calls)
