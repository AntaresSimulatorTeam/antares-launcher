from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.remote_environnement import iremote_environment
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


class RetrieveController:
    def __init__(
        self,
        repo: IDataRepo,
        env: iremote_environment.IRemoteEnvironment,
        file_manager: FileManager,
        display: IDisplay,
        state_updater: StateUpdater,
    ):
        self.repo = repo
        self.env = env
        self.file_manager = file_manager
        self.display = display
        self.state_updater = state_updater
        DataReporter(repo)
        logs_downloader = LogDownloader(
            env=self.env, file_manager=file_manager, display=self.display
        )
        final_zip_downloader = FinalZipDownloader(env=self.env, display=self.display)
        remote_server_cleaner = RemoteServerCleaner(env, display)
        zip_extractor = FinalZipExtractor(file_manager, display)
        self.study_retriever = StudyRetriever(
            state_updater,
            logs_downloader,
            final_zip_downloader,
            remote_server_cleaner,
            zip_extractor,
            DataReporter(repo),
        )

    @property
    def all_studies_done(self):
        """Checks if all the studies are done

        Returns:
            True if all the studies are done, False otherwise
        """
        studies = self.repo.get_list_of_studies()
        for study in studies:
            if not study.done:
                return False
        return True

    def retrieve_all_studies(self):
        """Retrieves all the studies and logs from the environment and process them

        Steps of processing:
        1. check job state
        2. download logs
        3. download results
        4. clean remote server
        5. extract result
        """
        studies = self.repo.get_list_of_studies()
        self.display.show_message(
            "Retrieving all studies",
            __name__ + "." + __class__.__name__,
        )
        for study in studies:
            if not study.done:
                self.study_retriever.retrieve(study)
        if self.all_studies_done:
            self.display.show_message(
                "Everything is done",
                __name__ + "." + __class__.__name__,
            )
        return self.all_studies_done
