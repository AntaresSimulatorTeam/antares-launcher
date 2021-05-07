from dataclasses import asdict
from unittest import mock

import pytest

import antareslauncher.use_cases
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch.study_submitter import StudySubmitter


class TestStudySubmitter:
    def setup_method(self):
        self.remote_env = mock.Mock(spec_set=IRemoteEnvironment)
        self.display_mock = mock.Mock(spec_set=IDisplay)
        self.study_submitter = StudySubmitter(self.remote_env, self.display_mock)

    @pytest.mark.unit_test
    def test_submit_study_shows_message_if_submit_succeeds(self):
        self.remote_env.submit_job = mock.Mock(return_value=42)
        study = StudyDTO(path="hello")

        new_study = self.study_submitter.submit_job(study)

        expected_message = f'"hello": was submitted'
        self.display_mock.show_message.assert_called_once_with(
            expected_message, mock.ANY
        )
        assert new_study.job_id == 42

    @pytest.mark.unit_test
    def test_submit_study_shows_error_if_submit_fails_and_exception_is_raised(
        self,
    ):
        self.remote_env.submit_job = mock.Mock(return_value=None)
        study = StudyDTO(path="hello")

        with pytest.raises(
            antareslauncher.use_cases.launch.study_submitter.FailedSubmissionException
        ):
            self.study_submitter.submit_job(study)

        expected_error_message = f'"hello": was not submitted'
        self.display_mock.show_error.assert_called_once_with(
            expected_error_message, mock.ANY
        )

    @pytest.mark.unit_test
    def test_remote_env_not_called_if_study_has_already_a_jobid(self):
        self.remote_env.submit_job = mock.Mock()
        study = StudyDTO(path="hello")
        study.job_id = 42

        self.study_submitter.submit_job(study)

        self.remote_env.submit_job.assert_not_called()

    @pytest.mark.unit_test
    def test_remote_env_is_called_if_study_has_no_jobid(self):
        self.remote_env.submit_job = mock.Mock(return_value=42)
        study = StudyDTO(path="hello")
        study.zipfile_path = "ciao.zip"
        study.job_id = None

        new_study = self.study_submitter.submit_job(study)

        self.remote_env.submit_job.assert_called_once()
        first_call = self.remote_env.submit_job.call_args_list[0]
        first_argument = first_call[0][0]
        assert asdict(first_argument) == asdict(study)
        assert new_study.job_id is 42
