from unittest import mock
from unittest.mock import call

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
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
def test_given_a_submitted_study_then_study_flags_are_updated(started_flag, finished_flag, with_error_flag, status):
    env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
    env.get_job_state_flags = mock.Mock(return_value=(started_flag, finished_flag, with_error_flag))
    display = mock.Mock(spec=DisplayTerminal)

    my_study = StudyDTO(path="study_path", job_id=42)
    state_updater = StateUpdater(env, display)
    state_updater.run(my_study)

    message = f'"{my_study.name}": (JOBID={my_study.job_id}): {status}'

    display.show_message.assert_called_once_with(message, mock.ANY)
    assert my_study.started == started_flag
    assert my_study.finished == finished_flag
    assert my_study.with_error == with_error_flag
    assert my_study.job_state == status


@pytest.mark.unit_test
def test_given_a_non_submitted_study_then_get_job_state_flags_is_not_called():
    # given
    env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
    display = mock.Mock(spec=DisplayTerminal)

    my_study = StudyDTO(path="study_path", job_id=None)
    state_updater = StateUpdater(env, display)
    state_updater.run(my_study)

    message = f'"{my_study.name}": Job was NOT submitted'
    env.get_job_state_flags.assert_not_called()
    display.show_error.assert_called_once_with(message, mock.ANY)


@pytest.mark.unit_test
def test_given_a_done_study_then_get_job_state_flags_is_not_called():
    # given
    env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
    env.get_job_state_flags = mock.Mock(return_value=(True, False, False))
    display = mock.Mock(spec=DisplayTerminal)

    my_study = StudyDTO(path="study_path", job_id=42, done=True)
    state_updater = StateUpdater(env, display)
    state_updater.run(my_study)

    message = f'"{my_study.name}": (JOBID={my_study.job_id}): everything is done'
    env.get_job_state_flags.assert_not_called()
    display.show_message.assert_called_once_with(message, mock.ANY)


@pytest.mark.unit_test
def test_state_updater_run_on_empty_list_of_studies_write_one_message():
    env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
    display = mock.Mock(spec=DisplayTerminal)

    state_updater = StateUpdater(env, display)
    state_updater.run_on_list([])

    message = "Checking status of the studies:"
    display.show_message.assert_called_once_with(message, mock.ANY)


@pytest.mark.unit_test
def test_with_a_list_of_one_submitted_study_run_on_list_calls_run_once_on_study():
    env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
    env.get_job_state_flags = mock.Mock(return_value=(1, 2, 3))
    display = mock.Mock(spec=DisplayTerminal)

    my_study1 = StudyDTO(path="study_path1", job_id=1)
    study_list = [my_study1]
    state_updater = StateUpdater(env, display)
    state_updater.run_on_list(study_list)

    env.get_job_state_flags.assert_called_once_with(my_study1)


@pytest.mark.unit_test
def test_run_on_list_calls_run_on_all_submitted_studies_of_the_list():
    env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
    env.get_job_state_flags = mock.Mock(return_value=(1, 2, 3))
    display = mock.Mock(spec=DisplayTerminal)

    my_study1 = StudyDTO(path="study_path1", job_id=1)
    my_study2 = StudyDTO(path="study_path2", job_id=None)
    my_study3 = StudyDTO(path="study_path3", job_id=2)
    study_list = [my_study1, my_study2, my_study3]
    state_updater = StateUpdater(env, display)
    state_updater.run_on_list(study_list)

    calls = [call(my_study1), call(my_study3)]
    env.get_job_state_flags.assert_has_calls(calls)


@pytest.mark.unit_test
def test_run_on_list_calls_run_start__processing_studies_that_are_done():
    env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
    env.get_job_state_flags = mock.Mock(return_value=(True, False, False))
    display = mock.Mock(spec=DisplayTerminal)

    my_study1 = StudyDTO(path="study_path1", job_id=1, done=False)
    my_study2 = StudyDTO(path="study_path2", job_id=None)
    my_study3 = StudyDTO(path="study_path3", job_id=2, done=True)
    study_list = [my_study1, my_study2, my_study3]
    state_updater = StateUpdater(env, display)
    state_updater.run_on_list(study_list)

    welcome_message = "Checking status of the studies:"
    message1 = f'"{my_study1.name}": (JOBID={my_study1.job_id}): Running'
    message3 = f'"{my_study3.name}": (JOBID={my_study3.job_id}): everything is done'
    calls = [
        call(welcome_message, mock.ANY),
        call(message3, mock.ANY),
        call(message1, mock.ANY),
    ]
    display.show_message.assert_has_calls(calls)
