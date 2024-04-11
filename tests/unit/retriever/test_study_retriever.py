from unittest import mock

import pytest

from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.clean_remote_server import RemoteServerCleaner
from antareslauncher.use_cases.retrieve.download_final_zip import FinalZipDownloader
from antareslauncher.use_cases.retrieve.final_zip_extractor import FinalZipExtractor
from antareslauncher.use_cases.retrieve.log_downloader import LogDownloader
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater
from antareslauncher.use_cases.retrieve.study_retriever import StudyRetriever


class TestStudyRetriever:
    def setup_method(self):
        env = mock.Mock(spec_set=RemoteEnvironmentWithSlurm)
        display = mock.Mock(spec_set=DisplayTerminal)
        repo = mock.Mock(spec_set=DataRepoTinydb)
        self.reporter = DataReporter(repo)
        self.state_updater = StateUpdater(env, display)
        self.logs_downloader = LogDownloader(env, display)
        self.final_zip_downloader = FinalZipDownloader(env, display)
        self.remote_server_cleaner = RemoteServerCleaner(env, display)
        self.zip_extractor = FinalZipExtractor(display)
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
    def test_given_study_with_error_study_is_still_in_error(self):
        env = mock.Mock()
        display = mock.Mock()
        self.state_updater = StateUpdater(env=env, display=display)
        study_with_error = StudyDTO(path="hello", with_error=True)
        self.study_retriever.retrieve(study_with_error)
        assert study_with_error.with_error

    @pytest.mark.unit_test
    def test_retrieve_study(self):
        """
        This test function simulates the retrieval process of a study and verifies
        that various components and states are updated correctly.

        Test cases covered:
        - State updater
        - Logs downloader
        - Final zip downloader
        - Remote server cleaner
        - Zip extractor
        - Reporter
        """
        study = StudyDTO(path="hello")

        def state_updater_run(study_: StudyDTO):
            study_.job_id = 42
            study_.started = True
            study_.finished = True
            study_.with_error = False
            return study_

        self.state_updater.run = mock.Mock(side_effect=state_updater_run)

        def logs_downloader_run(study_: StudyDTO):
            study_.logs_downloaded = True
            return study_

        self.logs_downloader.run = mock.Mock(side_effect=logs_downloader_run)

        def final_zip_downloader_download(study_: StudyDTO):
            study_.local_final_zipfile_path = "final-zipfile.zip"
            return study_

        self.final_zip_downloader.download = mock.Mock(side_effect=final_zip_downloader_download)

        def remote_server_cleaner_clean(study_: StudyDTO):
            study_.remote_server_is_clean = True
            return study_

        self.remote_server_cleaner.clean = mock.Mock(side_effect=remote_server_cleaner_clean)

        def zip_extractor_extract_final_zip(study_: StudyDTO):
            study_.final_zip_extracted = True
            return study_

        self.zip_extractor.extract_final_zip = mock.Mock(side_effect=zip_extractor_extract_final_zip)
        self.reporter.save_study = mock.Mock(return_value=True)

        self.study_retriever.retrieve(study)

        expected = StudyDTO(
            path="hello",
            job_id=42,
            done=True,
            started=True,
            finished=True,
            with_error=False,
            logs_downloaded=True,
            local_final_zipfile_path="final-zipfile.zip",
            remote_server_is_clean=True,
            final_zip_extracted=True,
        )
        self.reporter.save_study.assert_called_once_with(expected)
