from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.retrieve.clean_remote_server import RemoteServerCleaner
from antareslauncher.use_cases.retrieve.download_final_zip import FinalZipDownloader
from antareslauncher.use_cases.retrieve.final_zip_extractor import FinalZipExtractor
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

    def retrieve(self, study: StudyDTO):
        if not study.done:
            try:
                self.state_updater.run(study)
                self.logs_downloader.run(study)
                self.final_zip_downloader.download(study)
                self.remote_server_cleaner.clean(study)
                self.zip_extractor.extract_final_zip(study)
                study.done = study.with_error or (
                    study.logs_downloaded
                    and bool(study.local_final_zipfile_path)
                    and study.remote_server_is_clean
                    and study.final_zip_extracted
                )

            except Exception as e:
                # The exception is not re-raised, but the job is marked as failed
                study.with_error = True
                study.job_state = f"Internal error: {e}"

            finally:
                self.reporter.save_study(study)
