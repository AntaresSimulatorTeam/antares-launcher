from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch.study_submitter import StudySubmitter


class TestStudySubmitter:
    @pytest.mark.parametrize("actual_job_id", [0, 123456])
    @pytest.mark.unit_test
    def test_submit_job__nominal_case(self, pending_study: StudyDTO, actual_job_id: int) -> None:
        # Given
        pending_study.job_id = actual_job_id
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.submit_job = mock.Mock(return_value=987654)
        display = mock.Mock(spec=DisplayTerminal)
        submitter = StudySubmitter(env, display)

        # When
        submitter.submit_job(pending_study)

        # Then
        if actual_job_id:
            # The study job_id is not changed
            assert pending_study.job_id == actual_job_id
            # The display shows a message
            display.show_message.assert_called_once()
            display.show_error.assert_not_called()
        else:
            # The study job_id is changed
            assert pending_study.job_id == 987654
            # The display shows a message
            display.show_message.assert_called_once()
            display.show_error.assert_not_called()

    @pytest.mark.unit_test
    def test_submit_job__error_case(self, pending_study: StudyDTO) -> None:
        # Given
        pending_study.job_id = 0
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.submit_job = mock.Mock(return_value=0)
        display = mock.Mock(spec=DisplayTerminal)
        submitter = StudySubmitter(env, display)

        # When
        submitter.submit_job(pending_study)

        # Then
        # The study job_id is not changed
        assert pending_study.job_id == 0
        # The display shows an error
        display.show_message.assert_not_called()
        display.show_error.assert_called_once()
