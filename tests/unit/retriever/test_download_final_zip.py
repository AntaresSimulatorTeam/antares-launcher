from copy import copy
from pathlib import Path
from unittest import mock
from unittest.mock import call

import pytest

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.download_final_zip import (
    FinalZipDownloader,
    FinalZipNotDownloadedException,
)


class TestFinalZipDownloader:
    def setup_method(self):
        self.remote_env = mock.Mock(spec_set=IRemoteEnvironment)
        self.display_mock = mock.Mock(spec_set=IDisplay)
        self.final_zip_downloader = FinalZipDownloader(
            self.remote_env, self.display_mock
        )

    @pytest.fixture(scope="function")
    def successfully_finished_zip_study(self):
        return StudyDTO(
            path="path/hello",
            started=True,
            finished=True,
            with_error=False,
            job_id=42,
        )

    @pytest.mark.unit_test
    def test_download_study_shows_message_if_succeeds(
        self, successfully_finished_zip_study
    ):
        final_zipfile_path = "results.zip"
        self.remote_env.download_final_zip = mock.Mock(return_value=final_zipfile_path)

        self.final_zip_downloader.download(successfully_finished_zip_study)
        expected_message1 = '"hello": downloading final ZIP...'
        expected_message2 = '"hello": Final ZIP downloaded'
        calls = [
            call(expected_message1, mock.ANY),
            call(expected_message2, mock.ANY),
        ]
        self.display_mock.show_message.assert_has_calls(calls)

    @pytest.mark.unit_test
    def test_download_study_shows_error_and_raises_exceptions_if_failure(
        self, successfully_finished_zip_study
    ):
        self.remote_env.download_final_zip = mock.Mock(return_value=None)

        with pytest.raises(FinalZipNotDownloadedException):
            self.final_zip_downloader.download(successfully_finished_zip_study)

        expected_welcome_message = '"hello": downloading final ZIP...'
        expected_error_message = '"hello": Final ZIP not downloaded'
        self.display_mock.show_message.assert_called_once_with(
            expected_welcome_message, mock.ANY
        )
        self.display_mock.show_error.assert_called_once_with(
            expected_error_message, mock.ANY
        )

    @pytest.mark.unit_test
    def test_remote_env_not_called_if_final_zip_already_downloaded(self):
        self.remote_env.download_final_zip = mock.Mock()
        downloaded_study = StudyDTO("hello")
        downloaded_study.local_final_zipfile_path = "results.zip"

        new_study = self.final_zip_downloader.download(downloaded_study)

        self.remote_env.download_final_zip.assert_not_called()
        assert new_study == downloaded_study

    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "finished,with_error",
        [
            (False, False),
            (True, True),
        ],
    )
    def test_remote_env_not_called_if_final_zip_not_successfully_finished(
        self, finished, with_error
    ):
        self.remote_env.download_final_zip = mock.Mock()
        not_finished_study = StudyDTO("hello", finished=finished, with_error=with_error)

        new_study = self.final_zip_downloader.download(not_finished_study)

        self.remote_env.download_final_zip.assert_not_called()
        assert new_study == not_finished_study

    @pytest.mark.unit_test
    def test_remote_env_is_called_if_final_zip_not_yet_downloaded(
        self, successfully_finished_zip_study
    ):
        final_zipfile_path = "results.zip"
        self.remote_env.download_final_zip = mock.Mock(return_value=Path(final_zipfile_path))

        new_study = self.final_zip_downloader.download(successfully_finished_zip_study)

        self.remote_env.download_final_zip.assert_called_once()
        first_call = self.remote_env.download_final_zip.call_args_list[0]
        first_argument = first_call[0][0]
        assert first_argument == successfully_finished_zip_study

        expected_final_study = copy(successfully_finished_zip_study)
        expected_final_study.local_final_zipfile_path = final_zipfile_path
        assert new_study == expected_final_study
