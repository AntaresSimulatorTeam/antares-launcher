from copy import copy
from pathlib import Path
from unittest import mock

import pytest

from antareslauncher.display.idisplay import IDisplay
from antareslauncher.remote_environnement import iremote_environment
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.log_downloader import LogDownloader


class TestLogDownloader:
    def setup_method(self):
        self.remote_env_mock = mock.Mock(spec=iremote_environment.IRemoteEnvironment)
        self.file_manager = mock.Mock()
        self.display_mock = mock.Mock(spec_set=IDisplay)
        self.log_downloader = LogDownloader(
            self.remote_env_mock, self.file_manager, self.display_mock
        )

    @pytest.fixture(scope="function")
    def started_study(self):
        study = StudyDTO(path="path/hello")
        study.started = True
        study.job_id = 42
        study.job_log_dir = "ROOT_LOG_DIR"
        return study

    def test_download_shows_message_if_successful(self, started_study):
        self.remote_env_mock.download_logs = mock.Mock(return_value=True)
        self.log_downloader.run(started_study)

        expected_message = '"hello": Logs downloaded'
        self.display_mock.show_message.assert_called_once_with(
            expected_message, mock.ANY
        )

    def test_download_shows_error_if_fails_and_only_study_logdir_is_changed(
        self, started_study
    ):
        self.remote_env_mock.download_logs = mock.Mock(return_value=False)
        log_dir_name = f"{started_study.name}_{started_study.job_id}"
        expected_job_log_dir = str(Path(started_study.job_log_dir) / log_dir_name)
        expected_study = copy(started_study)
        expected_study.job_log_dir = expected_job_log_dir

        new_study = self.log_downloader.run(started_study)

        expected_message = '"hello": Logs not downloaded'
        self.display_mock.show_error.assert_called_once_with(expected_message, mock.ANY)
        assert new_study == expected_study

    def test_file_manager_and_remote_env_not_called_if_study_not_started(self):
        self.remote_env_mock.download_logs = mock.Mock()
        self.file_manager.make_dir = mock.Mock()
        study = StudyDTO(path="hello")
        study.started = False
        self.log_downloader.run(study)

        self.remote_env_mock.download_logs.assert_not_called()
        self.file_manager.make_dir.assert_not_called()

    def test_file_manager_is_called_to_create_logdir_if_study_started(
        self, started_study
    ):
        self.remote_env_mock.download_logs = mock.Mock(return_value=True)
        self.file_manager.make_dir = mock.Mock()

        self.log_downloader.run(started_study)

        log_dir_name = f"{started_study.name}_{started_study.job_id}"
        expected_job_log_dir = str(Path(started_study.job_log_dir) / log_dir_name)
        self.file_manager.make_dir.assert_called_once_with(expected_job_log_dir)

    def test_make_manager_is_called_properly_even_if_logdir_was_already_previously_set(
        self, started_study
    ):
        self.remote_env_mock.download_logs = mock.Mock(return_value=True)
        self.file_manager.make_dir = mock.Mock()
        log_dir_name = f"{started_study.name}_{started_study.job_id}"
        expected_job_log_dir = str(Path(started_study.job_log_dir) / log_dir_name)
        started_study.job_log_dir = expected_job_log_dir

        expected_study = copy(started_study)
        expected_study.job_log_dir = expected_job_log_dir

        self.log_downloader.run(started_study)

        self.file_manager.make_dir.assert_called_once_with(expected_job_log_dir)

    def test_environment_download_logs_is_called_if_study_started(self, started_study):
        log_dir_name = f"{started_study.name}_{started_study.job_id}"
        log_path = Path(started_study.job_log_dir) / log_dir_name
        self.remote_env_mock.download_logs = mock.Mock(return_value=[log_path])

        expected_job_log_dir = str(log_path)
        expected_study = copy(started_study)
        expected_study.job_log_dir = expected_job_log_dir

        new_study = self.log_downloader.run(started_study)

        first_call = self.remote_env_mock.download_logs.call_args_list[0]
        first_argument = first_call[0][0]
        assert first_argument == expected_study
        assert new_study.job_log_dir == expected_job_log_dir
        assert new_study.logs_downloaded is True
