from unittest import mock

import pytest

from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch.study_zip_uploader import StudyZipfileUploader


class TestStudyZipfileUploader:
    @pytest.mark.parametrize("actual_sent_flag", [True, False])
    @pytest.mark.unit_test
    def test_upload__nominal_case(self, pending_study: StudyDTO, actual_sent_flag: bool) -> None:
        # Given
        pending_study.zip_is_sent = actual_sent_flag
        display = mock.Mock(spec=DisplayTerminal)
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.upload_file = mock.Mock(return_value=True)
        uploader = StudyZipfileUploader(env, display)

        # When
        uploader.upload(pending_study)

        # Then
        if actual_sent_flag:
            env.upload_file.assert_not_called()
            display.show_message.assert_called_once()
        else:
            env.upload_file.assert_called_once_with(pending_study.zipfile_path)
            assert display.show_message.call_count == 2
        display.show_error.assert_not_called()
        assert pending_study.zip_is_sent

    @pytest.mark.unit_test
    def test_upload__error_case(self, pending_study: StudyDTO) -> None:
        # Given
        display = mock.Mock(spec=DisplayTerminal)
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.upload_file = mock.Mock(return_value=False)
        uploader = StudyZipfileUploader(env, display)

        # When
        uploader.upload(pending_study)

        # Then
        env.upload_file.assert_called_once_with(pending_study.zipfile_path)
        assert display.show_message.call_count == 1
        assert display.show_error.call_count == 1
        assert not pending_study.zip_is_sent

    @pytest.mark.parametrize("actual_sent_flag", [True, False])
    @pytest.mark.unit_test
    def test_remove__nominal_case(self, pending_study: StudyDTO, actual_sent_flag: bool) -> None:
        # Given
        pending_study.zip_is_sent = actual_sent_flag
        display = mock.Mock(spec=DisplayTerminal)
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.remove_input_zipfile = mock.Mock(return_value=True)
        uploader = StudyZipfileUploader(env, display)

        # When
        uploader.remove(pending_study)

        # Then
        # NOTE: The remote ZIP file is always removed even if `zip_is_sent` is `False`.
        env.remove_input_zipfile.assert_called_once_with(pending_study)
        display.show_message.assert_called_once()
        display.show_error.assert_not_called()
        assert not pending_study.zip_is_sent

    @pytest.mark.unit_test
    def test_remove__error_case(self, pending_study: StudyDTO) -> None:
        # Given
        pending_study.zip_is_sent = True
        display = mock.Mock(spec=DisplayTerminal)
        env = mock.Mock(spec=RemoteEnvironmentWithSlurm)
        env.remove_input_zipfile = mock.Mock(return_value=False)
        uploader = StudyZipfileUploader(env, display)

        # When
        uploader.remove(pending_study)

        # Then
        env.remove_input_zipfile.assert_called_once_with(pending_study)
        display.show_message.assert_not_called()
        display.show_error.assert_called_once()
        assert pending_study.zip_is_sent
