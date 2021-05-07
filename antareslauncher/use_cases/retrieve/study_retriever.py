from antareslauncher.data_repo.data_reporter import DataReporter
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


class StudyRetriever:
    def __init__(
        self,
        state_updater: StateUpdater,
        logs_downloader: LogDownloader,
        final_zip_downloader: FinalZipDownloader,
        remote_server_cleaner: RemoteServerCleaner,
        zip_extractor: FinalZipExtractor,
        reporter: DataReporter,
    ):
        self.state_updater = state_updater
        self.logs_downloader = logs_downloader
        self.final_zip_downloader = final_zip_downloader
        self.remote_server_cleaner = remote_server_cleaner
        self.zip_extractor = zip_extractor
        self.reporter = reporter
        self._current_study: StudyDTO = None

    def _update_job_state_flags(self):
        self._current_study = self.state_updater.run(self._current_study)
        self.reporter.save_study(self._current_study)

    def _download_slurm_logs(self):
        self._current_study = self.logs_downloader.run(self._current_study)
        self.reporter.save_study(self._current_study)

    def _download_final_zip(self):
        self._current_study = self.final_zip_downloader.download(self._current_study)
        self.reporter.save_study(self._current_study)

    def _clean_remote_server(self):
        self._current_study = self.remote_server_cleaner.clean(self._current_study)
        self.reporter.save_study(self._current_study)

    def _extract_study_result(self):
        self._current_study = self.zip_extractor.extract_final_zip(self._current_study)
        self.reporter.save_study(self._current_study)

    def _check_if_done(self):
        done = self.check_if_study_is_done(self._current_study)
        self._current_study.done = done
        self.reporter.save_study(self._current_study)

    def retrieve(self, study: StudyDTO):
        self._current_study = study
        if not self._current_study.done:
            self._update_job_state_flags()
            self._download_slurm_logs()
            self._download_final_zip()
            self._clean_remote_server()
            self._extract_study_result()
            self._check_if_done()

    @staticmethod
    def check_if_study_is_done(study: StudyDTO):
        return study.with_error or (
            study.logs_downloaded
            and study.local_final_zipfile_path
            and study.remote_server_is_clean
            and study.final_zip_extracted
        )
