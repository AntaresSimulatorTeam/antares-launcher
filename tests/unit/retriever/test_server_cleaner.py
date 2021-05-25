from copy import copy
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.clean_remote_server import (
    RemoteServerCleaner,
    RemoteServerNotCleanException,
)


class TestServerCleaner:
    def setup_method(self):
        self.remote_env_mock = mock.Mock(spec=iremote_environment.IRemoteEnvironment)
        self.display_mock = mock.Mock(spec_set=IDisplay)
        self.remote_server_cleaner = RemoteServerCleaner(
            self.remote_env_mock, self.display_mock
        )

    @pytest.fixture(scope="function")
    def downloaded_zip_study(self):
        study = StudyDTO(
            path=Path("path") / "hello",
            started=True,
            finished=True,
            job_id=42,
            local_final_zipfile_path=str(Path("final") / "zip" / "path.zip"),
        )
        return study

    @pytest.mark.unit_test
    def test_clean_server_show_message_if_successful(self, downloaded_zip_study):
        self.remote_env_mock.clean_remote_server = mock.Mock(return_value=True)
        self.remote_server_cleaner.clean(downloaded_zip_study)

        expected_message = (
            f'"{downloaded_zip_study.name}": Clean remote server finished'
        )
        self.display_mock.show_message.assert_called_once_with(
            expected_message, mock.ANY
        )

    @pytest.mark.unit_test
    def test_clean_server_show_error_and_raise_exception_if_fails(
        self, downloaded_zip_study
    ):
        self.remote_env_mock.clean_remote_server = mock.Mock(return_value=False)

        with pytest.raises(RemoteServerNotCleanException):
            self.remote_server_cleaner.clean(downloaded_zip_study)

        expected_error = f'"{downloaded_zip_study.name}": Clean remote server failed'
        self.display_mock.show_error.assert_called_once_with(expected_error, mock.ANY)

    @pytest.mark.unit_test
    def test_remote_environment_not_called_if_final_zip_not_downloaded(self):
        self.remote_env_mock.clean_remote_server = mock.Mock()
        study = StudyDTO(path="hello")
        study.local_final_zipfile_path = ""
        new_study = self.remote_server_cleaner.clean(study)

        self.remote_env_mock.clean_remote_server.assert_not_called()
        assert new_study == study

        study.local_final_zipfile_path = None
        new_study = self.remote_server_cleaner.clean(study)

        self.remote_env_mock.clean_remote_server.assert_not_called()
        assert new_study == study

    @pytest.mark.unit_test
    def test_remote_environment_not_called_if_remote_server_is_already_clean(
        self,
    ):
        self.remote_env_mock.clean_remote_server = mock.Mock()
        study = StudyDTO(path="hello")
        study.local_final_zipfile_path = "hello.zip"
        study.remote_server_is_clean = True
        new_study = self.remote_server_cleaner.clean(study)

        self.remote_env_mock.clean_remote_server.assert_not_called()
        assert new_study == study

    @pytest.mark.unit_test
    def test_remote_environment_is_called_if_final_zip_is_downloaded(
        self, downloaded_zip_study
    ):
        self.remote_env_mock.clean_remote_server = mock.Mock(return_value=True)
        expected_study = copy(downloaded_zip_study)

        new_study = self.remote_server_cleaner.clean(downloaded_zip_study)
        first_call = self.remote_env_mock.clean_remote_server.call_args_list[0]
        first_argument = first_call[0][0]
        assert first_argument == expected_study
        assert new_study.remote_server_is_clean
