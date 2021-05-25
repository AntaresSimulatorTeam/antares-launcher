from antareslauncher.data_repo.data_reporter import DataReporter
from antareslauncher.data_repo.idata_repo import IDataRepo
from antareslauncher.display.idisplay import IDisplay
from antareslauncher.file_manager.file_manager import FileManager
from antareslauncher.remote_environnement.iremote_environment import (
    IRemoteEnvironment,
)
from antareslauncher.study_dto import StudyDTO
from antareslauncher.use_cases.launch.study_submitter import StudySubmitter
from antareslauncher.use_cases.launch.study_zip_cleaner import StudyZipCleaner
from antareslauncher.use_cases.launch.study_zip_uploader import (
    StudyZipfileUploader,
)
from antareslauncher.use_cases.launch.study_zipper import StudyZipper


class StudyLauncher:
    def __init__(
        self,
        zipper: StudyZipper,
        study_uploader: StudyZipfileUploader,
        zipfile_cleaner: StudyZipCleaner,
        study_submitter: StudySubmitter,
        reporter: DataReporter,
    ):
        self._zipper = zipper
        self._study_uploader = study_uploader
        self._zipfile_cleaner = zipfile_cleaner
        self._study_submitter = study_submitter
        self.reporter = reporter
        self._current_study: StudyDTO = None

    def _zip_study(self):
        self._current_study = self._zipper.zip(self._current_study)
        self.reporter.save_study(self._current_study)

    def _upload_zipfile(self):
        self._current_study = self._study_uploader.upload(self._current_study)
        self.reporter.save_study(self._current_study)

    def _remove_input_zipfile(self):
        if self._current_study.zip_is_sent is True:
            self._current_study = self._zipfile_cleaner.remove_input_zipfile(
                self._current_study
            )
        self.reporter.save_study(self._current_study)

    def _submit_job(self):
        self._current_study = self._study_submitter.submit_job(self._current_study)
        self.reporter.save_study(self._current_study)

    def launch_study(self, study):
        self._current_study = study
        self._zip_study()
        self._upload_zipfile()
        self._remove_input_zipfile()
        self._submit_job()


class LaunchController:
    def __init__(
        self,
        repo: IDataRepo,
        env: IRemoteEnvironment,
        file_manager: FileManager,
        display: IDisplay,
    ):
        self.repo = repo
        self.env = env
        self.file_manager = file_manager
        self.display = display
        zipper = StudyZipper(file_manager, display)
        study_uploader = StudyZipfileUploader(env, display)
        zipfile_cleaner = StudyZipCleaner(file_manager, display)
        study_submitter = StudySubmitter(env, display)
        self.study_launcher = StudyLauncher(
            zipper,
            study_uploader,
            zipfile_cleaner,
            study_submitter,
            DataReporter(repo),
        )

    def launch_all_studies(self):
        """Processes all the studies and send them to the server to process the job

        Steps of processing:

        1. zip the study

        2. upload the study

        3. submit the slurm job
        """
        studies = self.repo.get_list_of_studies()
        for study in studies:
            self.study_launcher.launch_study(study)
