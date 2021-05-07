from copy import copy
from unittest import mock
from unittest.mock import call

import pytest

from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.clean_remote_server import (
    RemoteServerCleaner,
)
from antareslauncher.use_cases.retrieve.download_final_zip import (
    FinalZipDownloader,
)
from antareslauncher.use_cases.retrieve.final_zip_extractor import (
    FinalZipExtractor,
)
from antareslauncher.use_cases.retrieve.log_downloader import LogDownloader
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater
from antareslauncher.use_cases.retrieve.study_retriever import StudyRetriever


class TestStudyRetriever:
    def setup_method(self):
        env = mock.Mock(spec_set=IRemoteEnvironment)
        display = mock.Mock(spec_set=IDisplay)
        file_manager = mock.Mock(spec_set=FileManager)
        repo = mock.Mock(spec_set=IDataRepo)
        self.reporter = DataReporter(repo)
        self.state_updater = StateUpdater(env, display)
        self.logs_downloader = LogDownloader(env, file_manager, display)
        self.final_zip_downloader = FinalZipDownloader(env, display)
        self.remote_server_cleaner = RemoteServerCleaner(env, display)
        self.zip_extractor = FinalZipExtractor(file_manager, display)
        self.study_retriever = StudyRetriever(
            self.state_updater,
            self.logs_downloader,
            self.final_zip_downloader,
            self.remote_server_cleaner,
            self.zip_extractor,
            self.reporter,
        )

    @pytest.mark.unit_test
    def test_given_done_study_nothing_is_done(self):
        self.state_updater.run = mock.Mock()
        self.logs_downloader.run = mock.Mock()
        self.final_zip_downloader.download = mock.Mock()
        self.remote_server_cleaner.clean = mock.Mock()
        self.reporter.save_study = mock.Mock()
        self.zip_extractor.extract_final_zip = mock.Mock()

        done_study = StudyDTO(path="hello", done=True)
        self.study_retriever.retrieve(done_study)

        self.state_updater.run.assert_not_called()
        self.logs_downloader.run.assert_not_called()
        self.final_zip_downloader.download.assert_not_called()
        self.remote_server_cleaner.clean.assert_not_called()
        self.reporter.save_study.assert_not_called()
        self.zip_extractor.extract_final_zip.assert_not_called()

    @pytest.mark.unit_test
    def test_given_a_not_done_studies_everything_is_called(self):
        study = StudyDTO(path="hello")
        study1 = StudyDTO(
            path="hello",
            job_id=42,
            started=True,
            finished=True,
            with_error=False,
        )
        self.state_updater.run = mock.Mock(return_value=study1)
        study2 = copy(study1)
        study2.logs_downloaded = True
        self.logs_downloader.run = mock.Mock(return_value=study2)
        study3 = copy(study2)
        study3.local_final_zipfile_path = "final-zipfile.zip"
        self.final_zip_downloader.download = mock.Mock(return_value=study3)
        study4 = copy(study3)
        study4.remote_server_is_clean = True
        self.remote_server_cleaner.clean = mock.Mock(return_value=study4)
        study5 = copy(study4)
        study5.final_zip_extracted = True
        self.zip_extractor.extract_final_zip = mock.Mock(return_value=study5)
        study6 = copy(study5)
        study6.done = True
        self.reporter.save_study = mock.Mock()

        self.study_retriever.retrieve(study)

        self.state_updater.run.assert_called_once_with(study)
        self.logs_downloader.run.assert_called_once_with(study1)
        self.final_zip_downloader.download.assert_called_once_with(study2)
        self.remote_server_cleaner.clean.assert_called_once_with(study3)
        self.zip_extractor.extract_final_zip.assert_called_once_with(study4)
        assert self.reporter.save_study.call_count == 6
        calls = self.reporter.save_study.call_args_list
        assert calls[0] == call(study1)
        assert calls[1] == call(study2)
        assert calls[2] == call(study3)
        assert calls[3] == call(study4)
        assert calls[4] == call(study5)
        assert calls[5] == call(study6)

    @staticmethod
    @pytest.mark.unit_test
    @pytest.mark.parametrize(
        "result, with_error,logs_downloaded, local_final_zipfile_path, remote_server_is_clean, final_zip_extracted",
        [
            (False, False, False, None, False, False),
            (True, True, False, None, False, False),
            (True, False, True, "path.zip", True, True),
        ],
    )
    def test_when_study_finished_with_error_check_if_study_is_done_returns_true(
        result,
        with_error,
        logs_downloaded,
        local_final_zipfile_path,
        remote_server_is_clean,
        final_zip_extracted,
    ):
        my_study = StudyDTO(path="hello", job_id=42, started=True, finished=True)
        my_study.with_error = with_error
        my_study.logs_downloaded = logs_downloaded
        my_study.local_final_zipfile_path = local_final_zipfile_path
        my_study.remote_server_is_clean = remote_server_is_clean
        my_study.final_zip_extracted = final_zip_extracted
        assert StudyRetriever.check_if_study_is_done(my_study) is result
