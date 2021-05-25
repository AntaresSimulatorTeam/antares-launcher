from copy import copy
from unittest import mock
from unittest.mock import call

import pytest

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch.study_zip_uploader import (
    StudyZipfileUploader,
    FailedUploadException,
)


class TestZipfileUploader:
    def setup_method(self):
        self.remote_env = mock.Mock(spec_set=IRemoteEnvironment)
        self.display_mock = mock.Mock(spec_set=IDisplay)
        self.study_uploader = StudyZipfileUploader(self.remote_env, self.display_mock)

    @pytest.mark.unit_test
    def test_upload_study_shows_message_if_upload_succeeds(self):
        self.remote_env.upload_file = mock.Mock(return_value=True)
        study = StudyDTO(path="hello")

        self.study_uploader.upload(study)

        expected_message1 = f'"hello": uploading study ...'
        expected_message2 = f'"hello": was uploaded'
        calls = [
            call(expected_message1, mock.ANY),
            call(expected_message2, mock.ANY),
        ]
        self.display_mock.show_message.assert_has_calls(calls)

    @pytest.mark.unit_test
    def test_upload_study_shows_error_if_upload_fails_and_exception_is_raised(
        self,
    ):
        self.remote_env.upload_file = mock.Mock(return_value=False)
        study = StudyDTO(path="hello")

        with pytest.raises(FailedUploadException):
            self.study_uploader.upload(study)

        expected_welcome_message = f'"hello": uploading study ...'
        expected_error_message = f'"hello": was not uploaded'
        self.display_mock.show_message.assert_called_once_with(
            expected_welcome_message, mock.ANY
        )
        self.display_mock.show_error.assert_called_once_with(
            expected_error_message, mock.ANY
        )

    @pytest.mark.unit_test
    def test_remote_env_not_called_if_upload_was_done(self):
        self.remote_env.upload_file = mock.Mock()
        study = StudyDTO(path="hello")
        study.zip_is_sent = True

        new_study = self.study_uploader.upload(study)

        self.remote_env.upload_file.assert_not_called()
        assert new_study == study

    @pytest.mark.unit_test
    def test_remote_env_is_called_if_upload_was_not_done(self):
        self.remote_env.upload_file = mock.Mock()
        study = StudyDTO(path="hello")
        study.zip_is_sent = False
        expected_study = copy(study)
        expected_study.zip_is_sent = True

        new_study = self.study_uploader.upload(study)

        self.remote_env.upload_file.assert_called_once_with(study.zipfile_path)
        assert new_study == expected_study
