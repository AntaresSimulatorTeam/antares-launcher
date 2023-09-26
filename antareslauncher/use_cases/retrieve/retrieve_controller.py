from antareslauncher.data_repo.data_repo_tinydb import DataRepoTinydb
from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.display.display_terminal import DisplayTerminal
from antareslauncher.remote_environnement.remote_environment_with_slurm import RemoteEnvironmentWithSlurm
from antareslauncher.use_cases.retrieve.clean_remote_server import RemoteServerCleaner
from antareslauncher.use_cases.retrieve.download_final_zip import FinalZipDownloader
from antareslauncher.use_cases.retrieve.final_zip_extractor import FinalZipExtractor
from antareslauncher.use_cases.retrieve.log_downloader import LogDownloader
from antareslauncher.use_cases.retrieve.state_updater import StateUpdater
from antareslauncher.use_cases.retrieve.study_retriever import StudyRetriever

LOG_NAME = f"{__name__}.RetrieveController"


class RetrieveController:
    def __init__(
        self,
        repo: DataRepoTinydb,
        env: RemoteEnvironmentWithSlurm,
        display: DisplayTerminal,
        state_updater: StateUpdater,
    ):
        self.repo = repo
        self.env = env
        self.display = display
        self.state_updater = state_updater
        logs_downloader = LogDownloader(env=self.env, display=self.display)
        final_zip_downloader = FinalZipDownloader(env=self.env, display=self.display)
        remote_server_cleaner = RemoteServerCleaner(env=self.env, display=self.display)
        zip_extractor = FinalZipExtractor(display=self.display)
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
        return all(study.done for study in studies)

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
        self.display.show_message("Retrieving all studies...", LOG_NAME)
        for study in studies:
            self.study_retriever.retrieve(study)
        if self.all_studies_done:
            self.display.show_message("All retrievals are done.", LOG_NAME)
        return self.all_studies_done
